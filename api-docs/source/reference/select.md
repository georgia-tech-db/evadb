# SELECT keyword

## Syntax

![Flow chart showing the syntax of the SELECT keyword](images/select.svg)

![Flow chart showing the syntax of the FROM keyword](images/from.svg)


## Example Queries

1. Search frames with a car

```mysql
SELECT id, frame FROM MyVideo WHERE ['car'] <@ FastRCNNObjectDetector(frame).labels;
```
2. Search frames with a pedestrian and a car

```mysql
SELECT id, frame FROM MyVideo WHERE ['pedestrian', 'car'] <@ FastRCNNObjectDetector(frame).labels;
```


```mysql
SELECT id, frame FROM MyVideo WHERE array_count(FastRCNNObjectDetector(frame).labels, 'car') > 3;
```

3. Search frames containing greater than 3 cars

```mysql
SELECT id, frame FROM DETRAC WHERE array_count(FastRCNNObjectDetector(frame).labels, 'car') > 3;
```
