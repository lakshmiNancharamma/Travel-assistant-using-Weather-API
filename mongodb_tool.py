from langchain.tools import tool
from database import get_hotels_collection


@tool
def search_hotels(
    city: str,
    max_price: float,
    price_condition: str = "under"
) -> list:
    """
    Search hotels from MongoDB based on city and price.
    """

    collection = get_hotels_collection()

    if price_condition == "above":
        price_query = {"$gt": max_price}

    elif price_condition == "exact":
        price_query = {"$eq": max_price}

    else:
        price_query = {"$lte": max_price}

    query = {
        "city": {
            "$regex": f"^{city}$",
            "$options": "i"
        },
        "pricePerNight": price_query
    }

    projection = {
        "_id": 0,
        "name": 1,
        "city": 1,
        "area": 1,
        "pricePerNight": 1,
        "rating": 1,
        "available": 1,
        "amenities": 1
    }

    hotels = list(
        collection.find(
            query,
            projection
        )
        .sort("pricePerNight", 1)
        .limit(10)
    )

    return hotels