# integration_paas
Casey Johnson, 2023

## Quickstart
```
docker-compose up --build
// navigate to localhost:8080
// login with user/pass = airflow/airflow
```

## Notes

In theory, I want to define an end-to-end API cronjob in just a JSON file. Source, transformations, destination - all in one place. Then when I deploy that JSON config, the data simply starts flowing.

In practice, this works if you don't need authentication and you don't need any transformations. Those are things I'm still working on.