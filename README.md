# C-ATOM; Click-based semi-automatic annotation tool for object detection in the maritime domain
This is the demo client implementation of C-ATOM; Click-based semi-automatic annotation tool for object detection in the maritime domain.
It is implemented and tested with python3.
## Usage
```
pip install -r requirements.txt
python CATOM_client.py
```

Load image Button: Load your image

Clicking attention points process:
Right click: Generate an attention point (Red circle) on the clicked position
Left click: Delete the attention point on the clicked position

Send attention point(s): Send your attention point(s) to the annotation server and receive the results

### Load Image
![화면 캡처 2022-05-03 095229](https://user-images.githubusercontent.com/18137494/166390086-43986970-eb83-47c6-bc47-a0798b71ec1e.png)


### Click attention points
![화면 캡처 2022-05-03 095251](https://user-images.githubusercontent.com/18137494/166390092-8c96bbea-1adb-4a6f-968b-124c58c62a97.png)


### Show final bounding boxes from the C-ATOM Server

![화면 캡처 2022-05-03 095309](https://user-images.githubusercontent.com/18137494/166390099-4ea13d33-cc1a-41f9-b367-a5898a5a86f7.png)
