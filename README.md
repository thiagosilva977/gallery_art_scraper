# heni_test

# Getting Started
run the ```main.py``` file

# Results
### Task 1
```
{'artist_name': 'Peter Doig', 'painting_name': "The Architect's Home in the Ravine ", 'price_realised_gbp': 'GBP 11,282,500', 'price_realised_usd': 'USD 16,370,908', 'price_estimated_gbp': 'GBP 10,000,000 - GBP 15,000,000', 'price_estimated_usd': '(USD 14,509,999 - USD 21,764,999)', 'url_painting_image': 'http://www.christies.com/lotfinderimages/D59730/peter_doig_the_architects_home_in_the_ravine_d5973059h.jpg', 'saledate_paiting': datetime.date(2016, 2, 11)}

```


### Task 2

```
[{'rawDim': '19×52cm', 'height': 19.0, 'width': 52.0, 'depth': None}, {'rawDim': '50 x 66,4 cm', 'height': 50.0, 'width': 66.0, 'depth': None}, {'rawDim': '168.9 x 274.3 x 3.8 cm (66 1/2 x 108 x 1 1/2 in.)', 'height': 168.9, 'width': 274.3, 'depth': 3.8}, {'rawDim': 'Sheet: 16 1/4 × 12 1/4 in. (41.3 × 31.1 cm) Image: 14 × 9 7/8 in. (35.6 × 25.1 cm)', 'height': 35.6, 'width': 25.1, 'depth': None}, {'rawDim': '5 by 5in', 'height': 12.7, 'width': 12.7, 'depth': None}]

```


### Task 3 
[XLSX File with collected data.](https://github.com/thiagosilva977/heni_test/blob/master/assets/collected_data_v2.xlsx?raw=true)

### Task 4 
```
Inner join, Left join, Right join, and Full join are different types of SQL joins that combine two or more 
tables based on a common column. These concepts are applicable to dataframes in Python as well.

Inner join: An inner join returns only the rows that have matching values in both tables. The result set 
contains only the rows that appear in both tables based on the join condition.

Left join: A left join returns all the rows from the left table and the matching rows from the right table. 
If there is no match, the result set will contain NULL values for the columns from the right table.

Right join: A right join is similar to a left join, except that it returns all the rows from the right table 
and the matching rows from the left table. If there is no match, the result set will contain NULL values for 
the columns from the left table.

Full join: A full join returns all the rows from both tables, whether there is a match or not. If there is no 
match, the result set will contain NULL values for the columns from the missing table.
        
 
 Using MYSQL to do the sql commands: 
        
        1. Add full airline name to the flights dataframe and show the arr_time, origin, dest and the name of the 
        airline.
        
        SELECT flights.arr_time, flights.origin, flights.dest, airlines.name
        FROM flights
        JOIN airlines ON flights.carrier = airlines.carrier;
    
        2. Filter resulting data.frame to include only flights containing the word JetBlue
        
        SELECT flights.arr_time, flights.origin, flights.dest, airlines.name
        FROM flights
        JOIN airlines ON flights.carrier = airlines.carrier
        WHERE airlines.name LIKE '%JetBlue%';
    
        
        3. Summarise the total number of flights by origin in ascending.
    
        SELECT flights.origin, COUNT(flights.origin) AS total_flights
        FROM flights
        GROUP BY flights.origin
        ORDER BY total_flights ASC;
        
        4. Filter resulting data.frame to return only origins with more than 100 flights.
        
        SELECT flights.origin, COUNT(flights.origin) AS total_flights
        FROM flights
        GROUP BY flights.origin
        HAVING total_flights > 100
        ORDER BY total_flights ASC;
    
        
```

# Feedback
I loved taking this test, it was really cool.

For me the difficulty was moderate.
The regex task was the most difficult part, especially for so some regex on task 3.
The first time I did the project so fast that I ended up skipping a few steps and leaving out some important details.
Now the project is much more complete, with better and more accurate data capture, error prevention and better data export.

About possible improvements: 
- Better parse on the information collected on task 3 (actual accuracy is 97%)
- Better use of Scrapy (Nowadays I use more a framework that I've built)
- Improve the presentation of the codes
- Follow the PEP8 standards a little more
- Be more clearer in the documentation


## Time report
![image](https://user-images.githubusercontent.com/11250089/219970297-07a92bf0-587f-4324-b609-7b0d33ec23c3.png)



