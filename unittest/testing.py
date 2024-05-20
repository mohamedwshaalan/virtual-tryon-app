import unittest
import requests
import time
class TestAPI(unittest.TestCase):
    def tearDown(self) -> None:
        return super().tearDown()
    def setUp(self) -> None:
        return super().setUp()
    def test_hoodmodel(self):
        url = 'http://127.0.0.1:5004/api/hood/1/1/1'
        start_time = time.time()  # Record the start time
        response = requests.get(url)
        end_time = time.time()  # Record the end time
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")

        # test invalid user id
        url = 'http://127.0.01:5004/api/hood/1/20/1'
        response = requests.get(url)
        self.assertEqual(response.status_code, 500)
        # test invalid item id
        
    
    def test_MICE(self):
        url = 'http://127.0.0.1:5001/generate'
        start_time = time.time()
        request_data = {"weight": 60, "height": 170,"hips": 90, "chest": 40, "waist": 80,"gender":"female"}
        response = requests.post(url, json=request_data)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")
        # test invalid missing dimension
        request_data = {"weight": 60, "height": 170,"hips": 90, "chest": 40}
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 500)
        # test invalid user id

    def test_comprecmodel(self):
        url = 'http://127.0.0.1:5005/recommend'
        start_time = time.time()
        request_data = {"item_id": 1}
        response = requests.get(url, params=request_data)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")
        # test invalid item id
        request_data = {"item_id": -1}
        response = requests.get(url, params=request_data)
        self.assertEqual(response.status_code, 500)
        
    
    def test_comprecmodel2(self):
        url = 'http://127.0.0.1:5005/recommend_for_you'
        start_time = time.time()
        request_data = {'user_id': 1}
        response = requests.get(url, params=request_data)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")

    def test_hmr_api(self):
        url = 'http://127.0.0.1:5002/infer'
        start_time = time.time()
        request_data = {'user_id': 1}
        files = {'image_file': open('test.jpg', 'rb')}
        response = requests.post(url, data=request_data, files=files)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")
        # test invalid input
        request_data = {'user_id': 1}
        files = {'image_file': open('test.txt', 'rb')}
        response = requests.post(url, data=request_data, files=files)
        self.assertEqual(response.status_code, 500)


    def test_rating_api(self):
        url = 'http://127.0.0.1:5003/predictrating'
        start_time = time.time()
        request_data = {'top': 'top.jpg', 'bottom': 'bottom.jpg', 'shoe': 'shoe.jpg', 'bag': 'bag.jpg', 'accessory': 'accessory.jpg'}
        response = requests.post(url, json=request_data)
        end_time = time.time()
        self.assertEqual(response.status_code, 200)
        latency = end_time - start_time
        print(f"Latency: {latency} seconds")
        # test invalid input
        request_data = {'top': 'top.jpg', 'bottom': 'bottom.jpg', 'shoe': 'shoe.jpg', 'bag': 'bag.jpg'}
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 500)
        # test invalid input
        request_data = {'top': 'top.jpg', 'bottom': 'bottom.jpg', 'shoe': 'shoe.jpg', 'bag': 'bag.jpg', 'accessory': 'accessory.txt'}
        response = requests.post(url, json=request_data)
        self.assertEqual(response.status_code, 500)
        

    





if __name__ == '__main__':
    unittest.main()
