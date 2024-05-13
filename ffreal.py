import os
import requests
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SEATS_KEY = os.getenv("SEATS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def main():
    user_prompt = "Find award availability on 15th June 2024 from LAX to LHR in economy class using bilt points"

    print('------- Request for custom function calling ----------')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_prompt}],
        tools=[{
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
        "description": "name of credit card partner associated with bank"
    },
    
},

                    "required": ["origin_airport", "destination_airport"]
                }
            }
        }],
        tool_choice="auto"
    )

    args = response.choices[0].message.tool_calls[0]['function']['arguments']
    parsed_args = args
    parsed_args = json.loads(parsed_args)  # In Python, this should already be a dictionary
    partners = json.load(open('./partners.json'))

    try:
        print('------- Request for External API ----------')
        print(parsed_args)
        #print(partners)
       
        params = {
                # "api_key": SEATS_KEY,
                "take": 10,
                "origin_airport": parsed_args['origin_airport'],
                "destination_airport": parsed_args['destination_airport'],
                "cabin": parsed_args.get('cabin'),
                "start_date": parsed_args['start_date'],
                "end_date": "2024-06-16", #parsed_args['end_date'],
                # "order_by": parsed_args['order_by']
            }
        headers = {
            'Partner-Authorization': SEATS_KEY,
        }
        api_result = requests.get(
            "https://seats.aero/partnerapi/search",
            params=params,
            headers=headers
        ).json()
    except Exception as error:
        print('Error running Seats.aero search request')
        print(error)
        return
    print('------- Request for natural language ----------')
    # natural_response = openai.ChatCompletion.create(
    #     model="gpt-4-turbo",
    #     messages=[
    #         {"role": "system", "content": f"" + user_prompt + "in natural language."},
    #         {"role": "user", "content": str(api_result['data'])},
    #         {"role": "user", "content": str(partners)}
    #     ],
    # )

    for flight in api_result["data"]:
        print("Date:", flight["Date"])
        print("Origin Airport:", flight["Route"]["OriginAirport"])
        print("Destination Airport:", flight["Route"]["DestinationAirport"])
        print("Airline:", flight["YAirlines"])
        print("Mileage Cost (Economy):", flight["YMileageCost"])
        print("Seats Available (Economy):", flight["YRemainingSeats"])
        print("Direct Flight (Economy):", "Yes" if flight["YDirect"] else "No")
        print()

    # print(natural_response.choices[0].message.content)

if __name__ == "__main__":
    main()