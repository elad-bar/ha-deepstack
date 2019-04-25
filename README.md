<h1>DeepStack</h1>
<h2>Description</h2>
Extending the integration to <a href="https://github.com/robmarkcole/HASS-Deepstack">DeepStack API</a>, written by <a href="https://github.com/robmarkcole">robmarkcole</a>


With the following changes:
* Removed by default displaying response time
* Support admin/api keys
* Support face endpoints - list, register, recognize, delete
* Support backup / restore endpoints
* Added SSL flag to define whether the URL should be accessible with HTTPS, by default (since there’s no support for that :slight_smile:) it set to False
* Added support for object detection (list available in <a href="http://dev.deepstack.cc/docs/python/objectdetection.html">DeepStack Developer Portal</a>) 
* Support to enable / disable face recognition
* Support to enable / disable object detection
* Support to detect person before recognize face (detect work faster with lower load on the system)

HA Events:
* image_processing.detect_face - when face found and in the confidence level defined
* deepstack.unknown_face_detected - when face is found but not recognized or lower than confidence level
* deepstack.object_detected - when object detected according to the targets defined, will return list of all the targets with counter per each in the event data

HA Services:
* Detect before recognized for face recognition
* Change confidence level (default is 80), I use it when there’s no light to reduce the level by 5 precent
* Display response time (True / False)
* Register face (name and path)
* Delete face (name)
* Backup (available only if admin_key provided)
* Restore (available only if admin_key provided)

<h2>Example</h2>
<pre>
configuration: 
    deepstack:
      host: !secret deepstack_host (Required)
      port: !secret deepstack_port (Required)
      ssl: !secret deepstack_is_ssl (Optional)
      admin_key: !secret deepstack_admin_key (Optional)
      api_key: !secret deepstack_api_key (Optional)
      unknown_directory: !secret deepstack_unknown_faces_directroy (Optional)
        
    image_processing:
      - platform: deepstack
        scan_interval: 1
        # Setting as true will create image_processing for face recognition
        face_recognition: true
        # Setting as true will create image_processing for object deteection
        face_recognition:
          enabled: true
          detect_first: false
        object_detection:
          enabled: true
          targets: 
            - "person"
        source:
          - entity_id: !secret deepstack_camera_entity_id
            name: !secret deepstack_camera_name
</pre>

<h2>Custom_updater</h2>
<pre>
custom_updater:
  track:
    - components
  component_urls:
    - https://raw.githubusercontent.com/elad-bar/ha-deepstack/master/deepstack.json
</pre>
