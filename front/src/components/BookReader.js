import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const BookReader = () => {
  const { id } = useParams();
  const [book, setBook] = useState({});
  const [text, setText] = useState('');
  const [idBlock, setIdBlock] = useState(0);
  const user = JSON.parse(localStorage.getItem('user'));

  const fetchText = async () => {
    try {
      const response = await axios.post('/get_text', { id_user: user.id_user, id_book: parseInt(id) });
      if (response.status === 200) {
        setText(response.data.text);
        setIdBlock(response.data.id_block);
      }
    } catch (error) {
      console.error("Fetch text error:", error);
    }
  };

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const response = await axios.post('/get_book', { id_user: user.id_user, id_book: parseInt(id) });
        if (response.status === 200) {
          setBook(response.data);
          fetchText();  // Вызов функции fetchText
        }
      } catch (error) {
        console.error("Fetch book error:", error);
      }
    };

    fetchBook();
  }, [id, user.id_user]);

  const handleNext = async () => {
    try {
      await axios.post('/next_block_text', { id_user: user.id_user, id_book: parseInt(id) });
      fetchText();  // Вызов функции fetchText
    } catch (error) {
      console.error("Next block error:", error);
    }
  };

  const handleBack = async () => {
    try {
      await axios.post('/back_block_text', { id_user: user.id_user, id_book: parseInt(id) });
      fetchText();  // Вызов функции fetchText
    } catch (error) {
      console.error("Back block error:", error);
    }
  };

  return (
    <div>
      <h2>{book.title}</h2>
      <p>{book.author}</p>
      <p>{book.description}</p>
      <div>{text}</div>
      <button onClick={handleBack}>Previous</button>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};

export default BookReader;
