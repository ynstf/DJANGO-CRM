# middleware.py
class CountryCodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the country code from the URL if it exists
        country_code = None
        path_parts = request.path.split('/')
        
        # Check if the first part of the path is a valid country code
        if len(path_parts) > 1 and len(path_parts[1]) == 2:  # e.g., 'ma', 'fr'
            country_code = path_parts[1]

        if country_code:
            # Store the country code in the request object
            request.country_code = country_code
            request.country_code_prefix = f"/{country_code}"
            # Modify the path_info to remove the country code
            request.path_info = '/' + '/'.join(path_parts[2:])
        else:
            # Default value for country_code_prefix when no country code is in the URL
            request.country_code_prefix = ''

        # Continue processing the request
        response = self.get_response(request)
        print(f"Country Code Prefix in View: {request.country_code_prefix}")
        
        return response
