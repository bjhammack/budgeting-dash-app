# Budgeting Dash App
A single page web application built on Dash, Python, a SQLite3 database, and CSS for budgeting expenses, income, and financial goals. I personally use it to keep track of my own financials, by hosting it on an Apache server I set up on a Raspberry Pi.

## Overview
This is a fullstack project that utilizes a Dash and CSS front end, Python and Dash middleware, and a SQLite3 database built using RDMS best practices.

### The App
The app currently has four main interactive components. The first is the login page, where a user that has been entered into the system can enter their username and password to access their account.
![Login Page](https://github.com/bjhammack/budgeting-dash-app/example_images/login_example.png)
The second is a summary tab that shows an overview of a users expenses by month and category, income by month and category, net income by month, and the current state of their balances.
![Summary Page](https://github.com/bjhammack/budgeting-dash-app/example_images/summary_example.png)
The third is an invoices tab that allows users to view all invoices they have created and to create new invoices that will automatically update their balances and summaries when entered.
![Invoices Page](https://github.com/bjhammack/budgeting-dash-app/example_images/invoices_example.png)
The last is a balances tab that allows users to view all of their balances, transfer funds from one balance to another, edit balances, and create new balances.
![Balance Page](https://github.com/bjhammack/budgeting-dash-app/example_images/balances_example.png)

### Future Additions
There are several new features currently in the pipeline being worked on, as well as several features still in the conceptual stage I would like to incorporate.
<ul>
	<li>Projections Tab that utilizes basic logistic regression to show the user their expenses for the entire year or future years</li>
	<li>Visuals Tab that displays interactive graphs that users can use to view and manipulate their financial data.</li>
	<li>Scheduled expenses/income that will be added to invoices via a schedule rather than manually.</li>
	<li>Portfolio Page that allows users to upload and analyze an investment portfolio.</li>
	<li>More robust user accounts that allow for email notifications, custom layouts, and additional features.</li>
	<li>Conversion to a Flask based app that hosts Dash components. This will allow for more robust web development practices to be employed and better scalability.</li>
</ul>

## FAQ
<ol>
	<li>Can I access this webapp?
		Unfortuantely, no. While having secured the webapp with a firewall, several DDOS protections, and web development best practices to ensure security, until I am 100% certain the app is safe and secure I would not want to risk my own or anyone's financial information by making it publicly available.</li>
