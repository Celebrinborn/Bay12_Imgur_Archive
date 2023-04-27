# Bay12Forums Archiver

This project is designed to archive the Bay12Forums after Imgur is taken down. The project involves running an app called app.py, either directly on your machine using Python or via running a provided Dockerfile.

## Usage

### Running app.py directly on your machine

1. Clone the project onto your machine.
2. Navigate to the project directory.
3.A (optional but recommended). Create an venv environment with the commands "python -m venv env" followed by ".\env\scripts\activate" If you do other stuff with python this will prevent any annoying pip installs and make it easy to delete everything when you are done.
3. Install the required dependencies by running the following command: `pip install -r requirements.txt`
4. Create a file called `url_list.txt` in the `data` directory. Populate it with threads. Note: they must be bay12forums sites and must only have a topic parameter
http://www.bay12forums.com/smf/index.php?topic=168375.msg8472151#msg8472151 would not work
http://www.bay12forums.com/smf/index.php?topic=168375 will work
5. Run the app by running the command `python app.py`.

### Running app.py via Docker NOT YET IMPLEMENTED!!!!!!

1. Clone the project onto your machine.
2. Install Docker.
3. Create a file called `url_list.txt` in the `data` directory.
4. Run the Docker container by running the command `docker run -v /path/to/data:/app/data -v /path/to/logs:/app/logs bay12archiver`.

Note that you'll need to replace `/path/to/data` and `/path/to/logs` with the actual paths to your `data` and `logs` directories.

## Performance

It takes an average of 5.5 seconds per image per post in the thread to archive a thread. Keep this in mind when running the app.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
