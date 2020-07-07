# User Service APIs

#### <u>Caveats:</u>
- **Required Fields** are fields that are required for a successful response.
- Fields not defined by the API docs are not allowed.

#### <u>Common Http Status Codes:</u>

| Status Code   | Reason |
| :-------------: |:-------------|
| 400           | Invalid request |
| 401           | Failed authorization |
| 403           | Forbidden request/access |
| 404           | Resource not found |
| 405           | Undefined resource (endpoint does not exist) |
| 500           | Internal server error |

## Create, Update, Retrieve, or Delete User [/users]

### Create User [POST]

- **Required field**: `email-address`

Below are objects that have _required field dependencies_. This means that if the
objects below are provided, they must include their corresponding required field(s).


+ Request (application/json)

    + Headers
        
            Authorization: Bearer YiQWTGmepobdc0SGUv0Kv9U1U2BB4b
    
    + Body
    
            {
                "users": [
                    {
                        "first_name": "Khurram",
                        "last_name": "Farooq",
                        "email": "k.farooq@example.com",
                        "phone": "6509887675",
                        "pickup_addresses": [
                            {
                                "labe": "home",
                                "address_line_1": "5334 band ave",
                                "address_line_2": "11th floor suite #5",
                                "city": "santa clara",
                                "state": "california",
                                "zip_code": "95344"
                            }
                        ],
                        "dropoff_addresses": [
                            {
                                "label": "home",
                                "address_line_1": "5334 band ave",
                                "address_line_2": "11th floor suite #5",
                                "city": "santa clara",
                                "state": "california",
                                "zip_code": "95344"
                            }
                        ] 
                    }
                ]
            }

+ Response 201 (application/json)

    + Body
    
            {
                "users": [
                    {
                        "id": 34
                    }
                ]
            }

### Update User [PATCH]

**<u>Using this action you can</u>**:
- Change any of user's records
- Add new records to an existing user

**<u>Note the following</u>**:
- New data will be **added** to user's existing records if _object-ID is not provided_.
- Data will be **updated** for the user if _object-ID is provided_.

- **Required field**: `id` (user's unique ID)

+ Request (application/json)

    + Headers
        
            Authorization: Bearer YiQWTGmepobdc0SGUv0Kv9U1U2BB4b
    
    + Body
        
            {
                "users": [
                    {
                        "id": 34,
                        "email": "k.farooq@gmail.com",
                    }
                ]
            }
     
+ Response 200 (application/json)

    + Body
            
            {
                "users": [
                    {
                        "id": 34
                    }
                ]
            }

+ Request (application/json)

    + Headers
        
            Authorization: Bearer YiQWTGmepobdc0SGUv0Kv9U1U2BB4b
    
    + Body
        
            {
                "users": [
                    {
                        "id": 34,
                        "pickup_addresses": [
                            {
                                "labe": "work",
                                "address_line_1": "34 Yelp Street",
                                "address_line_2": "17th floor suite #19",
                                "city": "San Francisco",
                                "state": "california",
                                "zip_code": "95344"
                            }
                        ]
                    }
                ]
            }
     
+ Response 200 (application/json)

    + Body
            
            {
                "users": [
                    {
                        "id": 34
                    }
                ]
            }

## Retrieve user via ID [/users/{id}]

### Retrieve user by ID [GET]

+ Parameters

    + id: 34 (required, integer) - user's unique ID

+ Request
    
    + Headers
        
            Authorization: Bearer YiQWTGmepobdc0SGUv0Kv9U1U2BB4b

+ Response 200 (application/json)


            {
                "users": [
                    {
                        "id": 34,
                        "first_name": "Khurram",
                        "last_name": "Farooq",
                        "email": "k.farooq@example.com",
                        "phone": "6509887675",
                        "pickup_addresses": [
                            {
                                "id": 64,
                                "labe": "home",
                                "address_line_1": "5334 band ave",
                                "address_line_2": "11th floor suite #5",
                                "city": "santa clara",
                                "state": "california",
                                "zip_code": "95344"
                            }
                        ],
                        "dropoff_addresses": [
                            {
                                "id": 63
                                "label": "home",
                                "address_line_1": "5334 band ave",
                                "address_line_2": "11th floor suite #5",
                                "city": "santa clara",
                                "state": "california",
                                "zip_code": "95344"
                            }
                        ] 
                    }
                ]
            }
