# santo banquete

Santo Banquete is a friend's company that make and deliver frozen food. They've been operating for over six months with great success, but they lacked a digital system to help them track and organize their actions. The idea is to create an internal website, mobile friendly, that can help them have information, track stock and orders and register clients and suppliers.


# the project

The main idea is to have databases and be able to modify, update and display them to facilitate for the users. Because of the need to handle database queries in basically every module of the app, I decided to use Django as the main framework. Django makes the queries shorter and have a good models module that made the code more organized. I also like the way it is structured and the documentation available is very helpful and complete.

For the database, I chose PostgreSQL due to its simplicity, reliability and it also has really good documentation. It worked really well with django.

During the development of the app, there was a need to have APIs to fetch and send data to the database. Since Django doesn't come with that possibility, I used the Django Rest framework to deal with it. Rest does require code changes and include the serializers modules to be able to use JSON and the APIs.

The last step was to render changes made by the user in the same page without the need to render it again. That's why and when I decided to use React. React is really a game changer when it comes to the frontend responsiveness. I didn't apply React to the whole front end, but only to certain parts of it, although I may refactor the whole app to use React, if more performance is needed.

# how to use it

First, you must have an user and password to be able to login. The app will be used internally by very few people, so it's important to have security over the data and prevent the access from unknown people.

The initial page has a simple menu that guides the user through all the app modules. It's all in Portuguese because the company is in Brazil.

<p align="center">
  <img src="https://github.com/fimanishi/santo_banquete/blob/master/files/Images/Screen%20Shot%202017-07-19%20at%2010.57.06%20PM.png?  raw=true">
</p>

In the menu you can choose to create a new order, record production or update the stock. The other functions are not available now. For example, this is an example of adding materials to the stock.

<p align="center">
  <img src="https://github.com/fimanishi/santo_banquete/blob/master/files/Images/Screen%20Shot%202017-07-19%20at%2011.15.17%20PM.png">
</p>

You can choose to update the stock with new items that were bought or to visualize and update the stock based on the routine checks that are done. In this case, the item was filtered and the update button was clicked, allowing the user to change the current value for the item in stock.

<p align="center">
<img src="https://github.com/fimanishi/santo_banquete/blob/master/files/Images/Screen%20Shot%202017-07-19%20at%2011.20.52%20PM.png">

<img src="https://github.com/fimanishi/santo_banquete/blob/master/files/Images/Screen%20Shot%202017-07-19%20at%2011.21.15%20PM.png">
</p>

The other modules function in a similar way, always prompting modals to check if the user wants to do the action requested and also gives him/her the ability to create and update items whenever necessary.

# challenges

This is quite an extensive project that hasn't been finalized yet. It started only with PostgreSQL and Django, adding Rest and React later. Adding them was quite challenging. I had to learn how to use the serializers in Rest to be able to use APIs and JSON. It required refactoring a big part of the code in Django. Now, pretty much all the data that move from backend to frontend and vice versa is done using APIs.

Adding React was also a big important step in the project. I knew that I wanted the app to be more responsive and React was the right tool for it. But most of the html and CSS were ready, so I decided to use React in only part of the frontend. It was also on purpose for me to create a situation that is probably different from a website fully created using only react. Initially it was complicated to pass data from React to other parts of the app, but after doing a few times, it became quite simple and quick. The downside of having only part of the app with React is that there is a need to build and import every time to test it.
The React repository can be found here https://github.com/fimanishi/santo_react.

Another challenge that I encountered was to have some data available for multiple views and also create a virtual cart that did not update the database until the user was ready to do so. For that, I used the API and the session storage in the browser and in Django. It proved to be really useful event though the session in Django is not able to store Decimal values and the session in the browser has array limitation.
