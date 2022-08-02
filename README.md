# Web crawler

A web crawler to crawl through a specific website and extract all the insightful data from individual event page. Then a `plot` is generated to visualize the data.


## instructions

The project is Dockerized. To start the project, Follow the instructions,

* Run the command
```
docker compose build --no-cache; docker compose run crawler
```
* Wait and follow the bar to complete `(Crawling!)` in the terminal. 
* After successful completion, a file named `plot.png` will be saved in the project directory.
