# coffee-analysis

## Description
We are a coffee company based in Southampton, UK :uk: , and are looking to improve where we source our coffee from. The quality of coffee :coffee: sourced from our existing suppliers has significantly reduced in recent years, so we want to change suppliers whilst maintaining our reputation as the best artisanal coffee place in town. We have obtained a wealth of coffee supplier data from the independent Coffee Quality Institute, but we lack the skills required to analyse the data to help us decide where to send our coffee buyers to negotiate a new supply.

We would like an answer to the following question: <ins>**"Which country should we send our buyers to?”**</ins>

## Pre-requisites
We have created a simplified version of the dataset, which contains the following variables:
|Variable | Class |	Description |
| ------- | --------- | ------- |
| species |	`character` |	Species of coffee bean (arabica or robusta) |
| owner	| `character` |	Owner of the farm |
| country_of_origin |	`character` |	Where the bean came from |
| farm_name |	`character` |	Name of the farm |
| lot_number | `character` |	Lot number of the beans tested |
| mill |	`character` |	Mill where the beans were processed |
| company |	`character` |	Company name |
| altitude |	`character` |	Altitude |
| region |	`character` |	Region where bean came from |
| producer |	`character` |	Producer of the roasted bean |
| number_of_bags |	`double` |	Number of bags tested |
| bag_weight |	`character` |	Bag weight tested |
| in_country_partner |	`character` |	Partner for the country |
| harvest_year |	`character` |	When the beans were harvested (year) |
| grading_date |	`character` |	When the beans were graded |
| owner_1 |	`character` |	Who owns the beans |
| variety |	`character` |	Variety of the beans |
| processing_method |	`character` |	Method for processing |
| aroma |	`double` |	Aroma grade |
| flavor | `double` |	Flavor grade |
| aftertaste |	`double` |	Aftertaste grade |
| acidity |	`double` |	Acidity grade |
| body | `double` |	Body grade |
| balance |	`double` |	Balance grade |
| uniformity |	`double` | Uniformity grade |
| clean_cup |	`double` |	Clean cup grade |
| sweetness |	`double` |	Sweetness grade |
| cupper_points |	`double` |	Cupper Points (higher score = superior quality) |
| moisture |	`double` |	Moisture Grade |

## Installation

## Usage

This program is intended to be used to find the optimal country for coffee buyers to visit based on the coffee bean quality in each country.
When run it will show statistics about the quality, processing and type of each bean and then it will output which country most of the best fitting beans come from. 

## Running Tests
To run the unit tests open `testing.py`, this should contain all the unit tests for this project. If no errors are asserted, then everything works 👍, yay!

## Maintainers

## Licence

## Authors
Lee Baker, Lilia, Penelope, Xavier

## Acknowledgements
