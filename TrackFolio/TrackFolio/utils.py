# this removes the cache page from the response
# so that after logging out, the user cannot go back to the previous page
def remove_cache(response):
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response