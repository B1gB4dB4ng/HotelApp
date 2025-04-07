from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_hotel
from db.models import Dbuser
from schemas import HotelBase, HotelDisplay, UpdateHotelResponse
from typing import Optional, List
from auth.oauth2 import get_current_user


router = APIRouter(prefix="/hotel", tags=["Hotel"])


@router.post("/submit", response_model=HotelDisplay)
def submit_hotel(
    request: HotelBase,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    # Call db_hotel.create_hotel and check for duplication
    new_hotel = db_hotel.create_hotel(db, request, owner_id=user.id)

    if not new_hotel:  # If None is returned (i.e., hotel already exists)
        raise HTTPException(
            status_code=400, detail="A hotel with this name and location already exists"
        )

    return new_hotel  # Proceed to return the newly created hotel if no duplication


# read one hotel
@router.get("/{id}", response_model=HotelDisplay)
def get_hotel(id: int, db: Session = Depends(get_db)):
    hotel = db_hotel.get_hotel(db, id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel



# Combine search and filter logic into one endpoint
@router.get(
    "/", description="Get filtered/searched hotels ", response_model=List[HotelDisplay]
)
def get_hotels(
    search_term: Optional[str] = None,
    location: Optional[str] = Query(None, min_length=1),
    owner_id: Optional[int] = None,
    is_approved: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    filters = {
        "search_term": search_term,
        "location": location.strip() if location else None,
        "skip": 0,
        "limit": 100,
    }

    if owner_id is not None:
        filters["owner_id"] = owner_id

    if is_approved is not None:
        filters["is_approved"] = is_approved

    return db_hotel.combined_search_filter(db, **filters)



"""
Previous version of get hotels with authorization
# Combine search and filter logic into one endpoint
@router.get(
    "/", description="Get filtered/searched hotels ", response_model=List[HotelDisplay]
)
def get_hotels(
    search_term: Optional[str] = None,
    location: Optional[str] = Query(None, min_length=1),
    is_approved: Optional[bool] = None,  # 
    view_own: Optional[bool] = None,  # New parameter for owners
    db: Session = Depends(get_db),
    current_user: Optional[Dbuser] = Depends(get_current_user),
):
    filters = {
        "search_term": search_term,
        "location": location.strip() if location else None,
        "skip": 0,
        "limit": 100,
    }

    if current_user is None:
        # Non-logged-in user
        filters["is_approved"] = True  # Only show approved hotels

    else:
        # Admin user
        if current_user.is_superuser:
            # Admin: No need for view_own parameter, they see all hotels (approved and non-approved)
            if is_approved is not None:
                filters["is_approved"] = is_approved

        else:
            # Logged-in regular user (Owner)
            if view_own:
                filters["owner_id"] = current_user.id  # Only show the user's own hotels
                
                if is_approved is not None :
                    filters["is_approved"] = is_approved # show the hotels in accordance with selected value of is_approved (False / True)
                    print(filters)
                else:
                    filters["is_approved"] = None  #show only approved hotels
                    print(filters)
            else:
        # Default case for owners - only approved hotels
                filters["is_approved"] = True 


    # Use the COMBINED function from db_hotel.py
    return db_hotel.combined_search_filter(db, **filters)

"""

# update hotels
@router.put(
    "/{id}",
    response_model=UpdateHotelResponse,
    summary="Update hotel",
    description="Only owner or super admin can update. Only Admin can approve hotel",
)
def update_hotel(
    id: int,
    request: HotelBase,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    hotel = db_hotel.get_hotel(db, id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this hotel"
        )

    if not user.is_superuser and request.is_approved != hotel.is_approved:
        raise HTTPException(
            status_code=403, detail="Only an admin can update is_approved."
        )

    updated_hotel = db_hotel.update_hotel(db, id, request)

    if not updated_hotel:
        raise HTTPException(status_code=500, detail="Failed to update hotel")

    return UpdateHotelResponse(
        message="Hotel updated successfully", hotel=updated_hotel
    )


### DELETE HOTEL (Only Owner or Super Admin)
@router.delete(
    "/{id}",
    summary="Remove hotel",
    description="Only owner or super admin can delete",
)
def delete_hotel(
    id: int,
    db: Session = Depends(get_db),
    user: Dbuser = Depends(get_current_user),
):
    hotel = db_hotel.get_hotel(db, id)

    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if hotel.owner_id != user.id and not user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this hotel"
        )

    # Call delete_hotel from db_hotel and get the result
    delete_message = db_hotel.delete_hotel(db, id)

    return {"message": delete_message}  # Return success message

