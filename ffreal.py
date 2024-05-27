import os   
import requests
import openai
import json
import jmespath
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SEATS_KEY = os.getenv("SEATS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def check_partner(dictionary, search_term,partner):
    # Convert search term to lowercase
    search_term_lower = search_term.lower()
    
    # Create a new dictionary with lowercase keys
    lower_dict = {k.lower(): v for k, v in dictionary.items()}
    
    # Check if the lowercase search term is present as a key in the dictionary
    if search_term_lower in lower_dict:
        # Check if the value associated with the key is None
        if lower_dict[search_term_lower] is None:
            return None
        else:
            return f"Transfer {search_term} points to {partner} at a {lower_dict[search_term_lower]} ratio."
    else:
        return None
    

def find_transfer_bonus(data, transfer_to, transfer_from):
    for item in data:
        if item["Transfer To"].lower() in transfer_to.lower() and item["Transfer From"].lower() in transfer_from.lower():
            return f"Transfer Bonus: {item['Bonus']} (Valid until {item['End Date']})"
    return None

class_mapping = {
    "economy": "Y",
    "premium economy": "W",
    "business": "J",
    "first": "F"
}


def main():
    user_prompt = "Find award availability on 1st august 2024 from eur to sfo in economy class using chase points"


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
        "description": "name of credit card partner associated with bank. e.g. amex, chase, citi, capital one, etc."
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
    parsed_args = json.loads(parsed_args)  
    partners = json.load(open('./partners.json'))
    scrape_data = json.load(open('./scrape_data.json'))

    try:

        #print(parsed_args.get('end_date'))
        #print(partners)
       
        params = {
                # "api_key": SEATS_KEY,
                "take": 10,
                "origin_airport": parsed_args['origin_airport'],
                "destination_airport": parsed_args['destination_airport'],
                "cabin": parsed_args['cabin'] if parsed_args.get('cabin') else 'economy',
                "start_date": parsed_args['start_date'],
                "end_date": parsed_args['end_date'] if parsed_args.get('end_date') else parsed_args['start_date'],
                "order_by": parsed_args['order_by'] if parsed_args.get('order_by') else 'lowest_mileage'
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
    
    class_name = parsed_args['cabin']
    class_code = class_mapping.get(class_name.lower())

    for flight in api_result["data"]:
        search_term = flight['Source']
        found_program = None
        

        for program, details in partners.items():
            if search_term in program.lower():
                found_program = (program, details)
                break

        
        if parsed_args.get('partner') and found_program:
            print(check_partner(found_program[1], parsed_args.get('partner'), found_program[0])) if check_partner(found_program[1], parsed_args.get('partner'), found_program[0]) else None
            print(find_transfer_bonus(scrape_data,found_program[0],parsed_args['partner'])) if find_transfer_bonus(scrape_data,found_program[0],parsed_args['partner']) else None
            
        
        
        if class_code and int(flight[f'{class_code}RemainingSeats']) != 0:
            print("Flight Information:")
            print(f"- Program: {flight['Source']}")
            print(f"- Date: {flight['Date']}")
            print(f"- Airline: {flight[f'{class_code}Airlines']}")
            print(f"- From: {flight['Route']['OriginAirport']} to {flight['Route']['DestinationAirport']}")
            print(f"- {class_name.capitalize()} Available: {'Yes' if flight[f'{class_code}Available'] else 'No'}")
            print(f"- Seats Available: {flight[f'{class_code}RemainingSeats']}")
            print(f"- Mileage Cost: {flight[f'{class_code}MileageCost']} (Direct Cost: {flight[f'{class_code}DirectMileageCost']})")
            print(f"- Direct Flight: {'Yes' if flight[f'{class_code}Direct'] else 'No'}")
            print("\n")

    

if __name__ == "__main__":
    main()