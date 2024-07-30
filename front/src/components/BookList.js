import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const BookList = () => {
  const [books, setBooks] = useState({ titles: [], id_books: [] });
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const response = await axios.post('http://localhost:5000/get_user', { login: user.login });
        if (response.status === 200) {
          setBooks(response.data);
        }
      } catch (error) {
        console.error("Fetch books error:", error);
      }
    };

    fetchBooks();
  }, [user]);

  return (
    <div>
      <h2>My Books</h2>
      <ul>
        {books.titles && books.titles.map((title, index) => (
          <li key={index}>
            <Link to={`/reader/${books.id_books[index]}`}>{title}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BookList;
