import React, { useState, useEffect } from 'react';
import axios from './axiosConfig';  // Импортируйте настроенный экземпляр Axios
import { useParams } from 'react-router-dom';

const BookReader = () => {
  const { id } = useParams();
  const [book, setBook] = useState({});
  const [text, setText] = useState('');
  const [idBlock, setIdBlock] = useState(0);
  const [mode, setMode] = useState('');
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
        const response = await axios.post('http://localhost:5000/get_book', { id_user: user.id_user, id_book: parseInt(id) });
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
      await axios.post('http://localhost:5000/next_block_text', { id_user: user.id_user, id_book: parseInt(id) });
      fetchText();  // Вызов функции fetchText
    } catch (error) {
      console.error("Next block error:", error);
    }
  };

  const handleBack = async () => {
    try {
      await axios.post('http://localhost:5000/back_block_text', { id_user: user.id_user, id_book: parseInt(id) });
      fetchText();  // Вызов функции fetchText
    } catch (error) {
      console.error("Back block error:", error);
    }
  };

  const handleChangeMode = async (e) => {
    const selectedMode = e.target.value;
    setMode(selectedMode);
    try {
      await axios.post('http://localhost:5000/change_mode', { id_user: user.id_user, id_book: parseInt(id), mode: selectedMode });
      fetchText();  // Вызов функции fetchText для обновления текста в соответствии с выбранным режимом
    } catch (error) {
      console.error("Change mode error:", error);
    }
  };

  return (
    <div>
      <h2>{book.title}</h2>
      <p>{book.author}</p>
      <p>{book.description}</p>
      <div>
        <label htmlFor="mode">Select Reading Mode: </label>
        <select id="mode" value={mode} onChange={handleChangeMode}>
          <option value="">--Select Mode--</option>
          <option value="summarization_time">Summarization Time</option>
          <option value="summarization">Summarization</option>
          <option value="questions_original_text">Questions Original Text</option>
          <option value="retelling">Retelling</option>
          <option value="test">Test</option>
          <option value="similar_books">Similar Books</option>
        </select>
      </div>
      <div>{text}</div>
      <button onClick={handleBack}>Previous</button>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};

export default BookReader;
