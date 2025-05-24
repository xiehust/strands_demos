from strands import tool
import boto3
import uuid
table_name = "restaurant-assistant-bookings"

@tool
def request_confirm(date: str, hour: str, restaurant_name:str, guest_name: str, num_guests: int) ->str:
    """Request confirmation from the customer before creating a booking

    Args:
        date (str): The date of the booking in the format YYYY-MM-DD.Do NOT accept relative dates like today or tomorrow. Ask for today's date for relative date.
        hour (str): the hour of the booking in the format HH:MM
        restaurant_name(str): name of the restaurant handling the reservation
        guest_name (str): The name of the customer to have in the reservation
        num_guests(int): The number of guests for the booking

    Returns:
    """
    return f"""Please confirm the booking information with the customer.
booking information:
    date:{date}
    hour:{hour}
    restaurant_name:{restaurant_name}
    guest_name:{guest_name}
    num_guests:{num_guests}
    """


@tool
def create_booking(date: str, hour: str, restaurant_name:str, guest_name: str, num_guests: int) -> str:
    """Create a new booking at restaurant_name after confirmed by the customer

    Args:
        date (str): The date of the booking in the format YYYY-MM-DD.Do NOT accept relative dates like today or tomorrow. Ask for today's date for relative date.
        hour (str): the hour of the booking in the format HH:MM
        restaurant_name(str): name of the restaurant handling the reservation
        guest_name (str): The name of the customer to have in the reservation
        num_guests(int): The number of guests for the booking
    Returns:
        Status of booking
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)


        results = f"Creating reservation for {num_guests} people at {restaurant_name}, {date} at {hour} in the name of {guest_name}"
        print(results)
        booking_id = str(uuid.uuid4())[:8]
        response = table.put_item(
            Item={
                'booking_id': booking_id,
                'restaurant_name': restaurant_name,
                'date': date,
                'name': guest_name,
                'hour': hour,
                'num_guests': num_guests,
                # 'status':'pending'
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f'Booking with ID {booking_id} created successfully'
        else:
            return f'Failed to create booking with ID {booking_id}'
    except Exception as e:
        print(e)
        return str(e)
