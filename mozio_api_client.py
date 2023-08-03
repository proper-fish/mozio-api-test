import aiohttp


class MozioAPIClient:
    search_handler = '/v2/search/'
    reservations_handler = '/v2/reservations/'

    def __init__(self, host: str, api_key: str):
        self.host = host
        self.headers = {
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }

    async def _post(self, url: str, json: dict | None) -> dict:
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            async with session.post(url=url, json=json) as resp:
                status = resp.status
                if status == 200 or status == 201 or status == 202:
                    return await resp.json()
                else:
                    raise Exception(f'Response Status: {status}. Message: {await resp.text()}')

    async def _get(self, url: str) -> dict:
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            async with session.get(url=url) as resp:
                status = resp.status
                if status == 200 or status == 201 or status == 202:
                    return await resp.json()
                else:
                    raise Exception(f'Response Status: {status}. Message: {await resp.text()}')

    async def _delete(self, url: str):
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout, headers=self.headers) as session:
            async with session.delete(url=url) as resp:
                status = resp.status
                if status == 200 or status == 201 or status == 202:
                    return await resp.json()
                else:
                    raise Exception(f'Response Status: {status}. Message: {await resp.text()}')

    async def search(self, json_input: dict) -> str:

        resp = await self._post(self.host + self.search_handler, json=json_input)

        return resp['search_id']

    async def poll_search(self, search_id: str) -> dict:
        resp = await self._get(self.host + f'/v2/search/{search_id}/poll/')

        return resp

    @staticmethod
    def find_best_fitting_offer(search_result: dict, provider_name: str):
        """Finds the offer with the fitting provider name
            and the lowest price"""

        results_with_prices = {}
        for result in search_result["results"]:
            if result["steps"][0]["details"]["provider_name"] == provider_name:
                # creating a dict item {result_id: price}
                results_with_prices[result["result_id"]] = \
                    float(result["steps"][0]["details"]["price"]["price"]["value"])

        min_price_result_id = min(results_with_prices, key=results_with_prices.get)

        return min_price_result_id

    async def create_reservation(self, reservation_input: dict, search_id: str, result_id: str) -> str:
        json_input = reservation_input.copy()
        json_input['search_id'] = search_id
        json_input['result_id'] = result_id

        print(json_input)

        resp = await self._post(self.host + self.reservations_handler, json=json_input)

        status = resp['status']

        if status == 'pending' or status == 'completed':
            return status
        else:
            raise Exception('booking failed')

    async def poll_reservations(self, search_id: str):
        resp = await self._get(self.host + f'/v2/reservations/{search_id}/poll/')

        print('debug poll_reservations:')
        print(resp)

        return resp

    async def cancel_reservation(self, reservation_id: str) -> None:
        await self._delete(self.host + f'/v2/reservations/{reservation_id}/')

        return
