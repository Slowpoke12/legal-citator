# legal-citator
Checks word documents for compliance with certain rules of legal citation
# citegen

Legal citation generator library

## Building / developing citegen

At present, legal-citator is buildable on Unix systems (Linux, OSX).

### Prerequisites

#### Install Mammoth

Mammoth is used to convert docx file to html

##### Debian/Ubuntu 

sudo pip install mammoth

#### Install BeautifulSoup

BeautifulSoup is used to organize footnotes in html.

##### Debian/Ubuntu 

sudo pip install beautifulsoup4

### Building

After [cloning the project locally]
(https://help.github.com/articles/fetching-a-remote/#clone),
run the following command from the root directory of the project:

`mvn package`
