# Import Odyssey Espresso Json file to [Visualizer](https://visualizer.coffee/)


### Example files
1. oe-test.json
    - [Argos Night Brew](https://visualizer.coffee/shots/43a23304-ced0-4603-8373-f95d34021086)
2. oe-scale-only.json
    - [Argos Scale only](https://visualizer.coffee/shots/f60016f5-4d97-4ab7-8db0-bff66aa03b07)
3. oe-transducer-only.json
    - [Argos Transducer only](https://visualizer.coffee/shots/387fe103-e561-43c2-aa0c-c178fab675b5)
4. oe-scale-transducer.json
    - [Argos Scale and transducer](https://visualizer.coffee/shots/16c0458d-1585-4210-9f72-6f2641621851)


### Instructions
- Add files to 'test' directory
- Use `python3 oe_translation.py`
- New files will show in 'test/output' directory
- Login to your [Visualizer](https://visualizer.coffee/shots) account and click '+ Upload'
- Drag files to upload window

### Webapp for testing
https://oevisualizer-etnazwej.b4a.run/
- No files saved on host platform.
- Input JSON saved temporarily in a database for processing, then purged 5 minutes later.