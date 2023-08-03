import asyncio
import time

from mozio_api_client import MozioAPIClient

mozio_api_host = 'https://api-testing.mozio.com'
mozio_api_key = '6bd1e15ab9e94bb190074b4209e6b6f9'  # publicly displayed bc it's a test task

search_input = {
    "start_address": "44 Tehama Street, San Francisco, CA, USA",
    "end_address": "SFO",
    "mode": "one_way",
    "pickup_datetime": "2023-12-01 15:30",
    "num_passengers": 2,
    "currency": "USD",
    "campaign": "Aliona Kozushkina"
}

provider_name = "Dummy External Provider"

reservation_input = {
    "email": "test@mail.ru",
    "phone_number": "+995551199900",
    "first_name": "Aliona",
    "last_name": "Kozushkina",
    "airline": "AA",
    "flight_number": "123"
}


async def script():
    api_client = MozioAPIClient(mozio_api_host, mozio_api_key)

    # creating a search
    search_id = await api_client.search(search_input)

    # getting search results
    full_search_result = []
    while True:
        search_result = await api_client.poll_search(search_id)
        full_search_result.extend(search_result["results"])
        if search_result["more_coming"] is True:
            time.sleep(2)
        else:
            break

    # choosing the offer according to provider & price conditions
    fitting_result_id = api_client.find_best_fitting_offer(full_search_result[0], provider_name)

    # creating a reservations for the chosen offer
    create_reservation_status = await api_client.create_reservation(reservation_input,
                                                                    search_id=search_id,
                                                                    result_id=fitting_result_id)

    while True:
        reservation = await api_client.poll_reservations(search_id)
        if reservation['status'] == 'pending':
            time.sleep(2)
        elif reservation['status'] == 'completed':
            break
        else:
            raise Exception('booking failed')

    reservation_id = reservation["reservations"][0]["id"]
    confirmation_number = reservation["reservations"][0]["confirmation_number"]

    # cancelling the reservation
    await api_client.cancel_reservation(reservation_id)

    # returning the reservation confirmation number
    return confirmation_number


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(script())
