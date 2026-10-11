import pytest


@pytest.mark.automotive
@pytest.mark.smoke
def test_add_2023_tesla_model_3_to_garage(automotive_page, search_results_page):
    # Step 1: Go to Amazon Automotive
    automotive_page.open_automotive()
    # Step 2: Open Your Garage
    automotive_page.open_your_garage()
    # Step 3: Add a 2023 Tesla Model 3
    automotive_page.open_add_vehicle_form()
    automotive_page.add_vehicle(year="2023", make="Tesla", model="Model 3")
    # Step 4: Vehicle should appear in the garage
    automotive_page.expect_vehicle_in_garage(year="2023", make="Tesla", model="Model 3")
    # Step 5: Log whether "More vehicle information needed" is on screen (does not fail)
    automotive_page.report_more_vehicle_information_needed()
    # Step 6: Search seat covers, sort lowest price, add that item to cart
    automotive_page.search("seat covers")
    search_results_page.sort_by_price_low_to_high()
    search_results_page.add_first_result_to_cart()
    automotive_page.expect_cart_not_empty()
