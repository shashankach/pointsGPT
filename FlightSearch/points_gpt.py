from .models import FlightSearchResult

import requests
from openai import OpenAI

client = OpenAI()
import json
import os

TRANSFER_PARTNERS_JSON_FILE = 'partners.json'

SEATS_AERO_API_KEY = os.getenv("SEATS_AERO_API_KEY")

FARE_CLASS_KEY = {
    "economy": "Y",
    "premium economy": "W",
    "business": "J",
    "first": "F"
}

OPENAI_SETUP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "MilesSearch",
            "description": "Extract mileage information from the user prompt",
            "parameters": { 
                "type": "object",
                "properties": {
                    "take": {
                        "type": "number",
                        "description": "The number of results to return"
                    },
                    "origin_airport": {
                        "type": "string",
                        "description": "The IATA code for the origin airport"
                    },
                    "destination_airport": {
                        "type": "string",
                        "description": "The IATA code for the destination airport"
                    },
                    "cabin": {
                        "type": "string",
                        "description": "The class of the cabin (economy, premium, business, or first)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "The start date for the flight search (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "The end date for the flight search (YYYY-MM-DD)"
                    },
                    "order_by": {
                        "type": "string",
                        "description": "The order by which to sort the results (e.g., lowest_mileage)"
                    },
                    "partner": {
                        "type": "string",
                        "description": "name of credit card partner associated with bank. e.g. amex, chase, citi, capital one, etc."
                    }
                },
                "required": ["origin_airport", "destination_airport"]
            }
        }
    }
]

class PointsGPT:
    TRANSFER_PARTNERS = json.load(open(TRANSFER_PARTNERS_JSON_FILE))
    @staticmethod
    def parse_args(prompt):
        try: 
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                tools=OPENAI_SETUP_TOOLS,
                tool_choice='auto'
                )
            args = json.loads(
                response.choices[0].message.tool_calls[0].function.arguments
            )
            args['cabin'] = args.get('cabin', 'economy').lower()
            args['take'] = int(args.get('take', 10))
            args['end_date'] = args.get('end_date', args.get('start_date', ''))
            args['order_by'] = args.get('order_by', 'lowest_mileage')
            return args
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def search_seats_aero_api(search_params):
        if not SEATS_AERO_API_KEY:
            raise Exception("SEATS_AERO_API_KEY environment variable is not set")
        query_url = "https://seats.aero/partnerapi/search"
        params = search_params.copy()

        response = requests.get(query_url, params=params, headers={
            "Partner-Authorization": SEATS_AERO_API_KEY
        }).json()
 
        fare_class = FARE_CLASS_KEY.get(params['cabin'])
        flight_list = []
        partners = json.load(open("partners.json"))
        bonus = json.load(open("scrape_data.json"))
        


        for flight_info in response['data']:

            found_program = None
            search_term = flight_info['Source']
            for program, details in partners.items():
                if search_term in program.lower().replace(' ', ''):
                    found_program = (program, details)
                    break
            
            if params['partner'] and found_program:
                partner_info = PointsGPT.get_partner_program(found_program[1],params['partner'],found_program[0]) if PointsGPT.get_partner_program(found_program[1],params['partner'],found_program[0]) else None
                bonus_info = PointsGPT.find_transfer_bonus(bonus,found_program[0],params['partner']) if PointsGPT.find_transfer_bonus(bonus,found_program[0],params['partner']) else None  
                print(bonus_info) 
            
            remaining_seats = int(flight_info[f'{fare_class}RemainingSeats'])
            if fare_class is not None and remaining_seats > 0:
                flight_list.append(
                    FlightSearchResult(
                        program=flight_info['Source'],
                        date=flight_info['Date'],
                        airline=flight_info[f'{fare_class}Airlines'],
                        origin=flight_info['Route']['OriginAirport'],
                        destination=flight_info['Route']['DestinationAirport'],
                        class_available=params['cabin'],
                        seats_available=remaining_seats,
                        mileage_cost=flight_info[f'{fare_class}MileageCost'],
                        direct_cost=flight_info[f'{fare_class}DirectMileageCost'],
                        direct_flight=flight_info[f'{fare_class}Direct'],
                        partner = partner_info,
                        bonus = bonus_info
                    )
                )
        return flight_list



    @staticmethod
    def get_partner_program(dictionary, search_term,partner):
        
        search_term_lower = search_term.lower()
        lower_dict = {k.lower(): v for k, v in dictionary.items()}

        
        if search_term_lower in lower_dict:
            if lower_dict[search_term_lower] is None:
                return None
            else:
                return f"Transfer {search_term} points to {partner} at a {lower_dict[search_term_lower]} ratio."
        else:
            return None
        
    @staticmethod
    def find_transfer_bonus(data, transfer_to, transfer_from):
        for item in data:
            if item["Transfer To"].lower().replace(' ','') in transfer_to.lower().replace(' ','') and transfer_from.lower() in item["Transfer From"].lower():
                return f"Transfer Bonus: {item['Bonus']} (Valid until {item['End Date']})"
        return None