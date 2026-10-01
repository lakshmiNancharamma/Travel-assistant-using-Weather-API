import re

from weather_tool import get_weather
from mongodb_tool import search_hotels
from calculator_tool import calculate


# =========================================================
# Extract city
# =========================================================
def extract_city(question: str):

    cities = [
        "Hyderabad",
        "Chennai",
        "Bangalore",
        "Bengaluru",
        "Mumbai",
        "Delhi",
        "Pune",
        "Kolkata",
        "Goa",
        "Jaipur"
    ]

    for city in cities:

        pattern = rf"\b{re.escape(city)}\b"

        if re.search(
            pattern,
            question,
            re.IGNORECASE
        ):
            return city

    return None


# =========================================================
# Extract days / nights
# =========================================================
def extract_days(question: str):

    pattern = r"(\d+)\s*(?:day|days|night|nights)"

    match = re.search(
        pattern,
        question,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return 1


# =========================================================
# Extract budget
# =========================================================
def extract_budget(question: str):

    patterns = [

        # ₹5000 / ₹ 5000
        r"₹\s*([\d,]+(?:\.\d+)?)",

        # Rs 5000 / Rs. 5000
        r"rs\.?\s*([\d,]+(?:\.\d+)?)",

        # rupees 5000
        r"rupees\s*([\d,]+(?:\.\d+)?)",

        # under 5000
        r"(?:under|below|less than|up to|upto|maximum|max)"
        r"\s*₹?\s*([\d,]+(?:\.\d+)?)",

        # above 5000
        r"(?:above|over|more than|greater than|higher than)"
        r"\s*₹?\s*([\d,]+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            question,
            re.IGNORECASE
        )

        if match:

            value = match.group(1)

            value = value.replace(",", "")

            return float(value)

    return None


# =========================================================
# Determine price condition
# =========================================================
# =========================================================
# Determine price condition
# =========================================================
def extract_price_condition(question: str):

    question_lower = question.lower()

    # ABOVE PRICE
    above_phrases = [
        "above",
        "over",
        "more than",
        "greater than",
        "higher than"
    ]

    if any(
        phrase in question_lower
        for phrase in above_phrases
    ):
        return "above"

    # EXACT PRICE
    exact_phrases = [
        "exactly",
        "exact",
        "equal to",
        "equal",
        "at ₹",
        "at rs",
        "at rupees"
    ]

    if any(
        phrase in question_lower
        for phrase in exact_phrases
    ):
        return "exact"

    # UNDER PRICE
    under_phrases = [
        "under",
        "below",
        "less than",
        "up to",
        "upto",
        "maximum",
        "max"
    ]

    if any(
        phrase in question_lower
        for phrase in under_phrases
    ):
        return "under"

    # Default
    return "under"


# =========================================================
# Check weather request
# =========================================================
def is_weather_request(question: str):

    weather_words = [
        "weather",
        "forecast",
        "temperature",
        "rain",
        "raining",
        "climate",
        "hot",
        "cold"
    ]

    question_lower = question.lower()

    return any(
        word in question_lower
        for word in weather_words
    )


# =========================================================
# Check hotel request
# =========================================================
def is_hotel_request(question: str):

    hotel_words = [
        "hotel",
        "hotels",
        "stay",
        "accommodation",
        "room"
    ]

    question_lower = question.lower()

    return any(
        word in question_lower
        for word in hotel_words
    )


# =========================================================
# Check calculation request
# =========================================================
def is_calculation_request(question: str):

    calculation_words = [
        "calculate",
        "calculation",
        "total",
        "cost",
        "how much",
        "amount"
    ]

    question_lower = question.lower()

    return any(
        word in question_lower
        for word in calculation_words
    )


# =========================================================
# Format weather
# =========================================================
def format_weather(weather_result):

    return weather_result


# =========================================================
# Format hotel
# =========================================================
def format_hotel(
    hotel,
    nights,
    calculate_total
):

    name = hotel.get(
        "name",
        "Unknown Hotel"
    )

    city = hotel.get(
        "city",
        "Unknown"
    )

    area = hotel.get(
        "area",
        "Unknown"
    )

    price = hotel.get(
        "pricePerNight",
        0
    )

    rating = hotel.get(
        "rating",
        "N/A"
    )

    available = hotel.get(
        "available",
        True
    )

    amenities = hotel.get(
        "amenities",
        []
    )

    amenities_text = ", ".join(
        str(item)
        for item in amenities
    )

    result = f"""Name: {name}
City: {city}
Area: {area}
Price per night: ₹{price}
Rating: {rating}
Available: {available}
Amenities: {amenities_text}"""

    # -----------------------------------------------------
    # Calculator Tool
    # -----------------------------------------------------
    if calculate_total:

        expression = f"{price} * {nights}"

        total_cost = calculate.invoke(
            expression
        )

        result += (
            f"\nTotal cost for {nights} night(s): "
            f"₹{total_cost}"
        )

    return result


# =========================================================
# Main Travel Assistant
# =========================================================
def ask_agent(question: str):

    if not question.strip():

        return "Please enter a travel question."

    # -----------------------------------------------------
    # Extract information
    # -----------------------------------------------------
    city = extract_city(question)

    days = extract_days(question)

    budget = extract_budget(question)

    price_condition = extract_price_condition(
        question
    )

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------
    weather_result = None

    hotel_result = None

    # =====================================================
    # WEATHER TOOL
    # =====================================================
    if is_weather_request(question):

        if city:

            weather_result = get_weather.invoke(
                {
                    "city": city,
                    "days": days
                }
            )

        else:

            weather_result = (
                "Please provide a city name "
                "so I can check the weather."
            )

    # =====================================================
    # MONGODB HOTEL TOOL
    # =====================================================
    if is_hotel_request(question):

        if not city:

            hotel_result = (
                "Please provide a city name "
                "so I can search for hotels."
            )

        elif budget is None:

            hotel_result = (
                "Please provide a hotel budget "
                "so I can search for hotels."
            )

        else:

            # -------------------------------------------------
            # Search MongoDB
            # -------------------------------------------------
            hotels = search_hotels.invoke(
                {
                    "city": city,
                    "max_price": budget,
                    "price_condition": price_condition
                }
            )

            # -------------------------------------------------
            # Check whether calculation is required
            # -------------------------------------------------
            calculate_total = is_calculation_request(
                question
            )

            # -------------------------------------------------
            # No hotels found
            # -------------------------------------------------
            if not hotels:

                if price_condition == "above":

                    hotel_result = (
                        f"No hotels found in {city} "
                        f"above ₹{budget:.0f} per night."
                    )

                elif price_condition == "exact":

                    hotel_result = (
                        f"No hotels found in {city} "
                        f"at ₹{budget:.0f} per night."
                    )

                else:

                    hotel_result = (
                        f"No hotels found in {city} "
                        f"under ₹{budget:.0f} per night."
                    )

            # -------------------------------------------------
            # Hotels found
            # -------------------------------------------------
            else:

                formatted_hotels = []

                for hotel in hotels:

                    hotel_text = format_hotel(
                        hotel,
                        days,
                        calculate_total
                    )

                    formatted_hotels.append(
                        hotel_text
                    )

                hotel_result = "\n\n".join(
                    formatted_hotels
                )

    # =====================================================
    # COMBINED RESPONSE
    # =====================================================
    response_parts = []

    # -----------------------------------------------------
    # Weather
    # -----------------------------------------------------
    if weather_result:

        response_parts.append(
            weather_result
        )

    # -----------------------------------------------------
    # Hotels
    # -----------------------------------------------------
    if hotel_result:

        if price_condition == "above":

            heading = (
                f"Hotel options in {city} "
                f"above ₹{budget:.0f} per night:"
            )

        elif price_condition == "exact":

            heading = (
                f"Hotel options in {city} "
                f"at ₹{budget:.0f} per night:"
            )

        else:

            heading = (
                f"Hotel options in {city} "
                f"under ₹{budget:.0f} per night:"
            )

        response_parts.append(
            f"{heading}\n\n"
            f"{hotel_result}"
        )

    # -----------------------------------------------------
    # Nothing detected
    # -----------------------------------------------------
    if not response_parts:

        return (
            "I can help you with weather forecasts, "
            "hotel searches, and travel cost calculations."
        )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------
    return "\n\n".join(
        response_parts
    )