import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Login from './components/Login';
import BookList from './components/BookList';
import BookReader from './components/BookReader';

function App() {
    console.log(1)
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login/>}/>
                <Route path="/books" element={<BookList/>}/>
                <Route path="/reader/:id" element={<BookReader/>}/>
            </Routes>
        </Router>
    );
}

export default App;
