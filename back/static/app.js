document.addEventListener('DOMContentLoaded', function() {
    const loginInput = document.getElementById('login-input');
    const loginButton = document.getElementById('login-button');
    const bookListSection = document.getElementById('book-list');
    const bookDetailSection = document.getElementById('book-detail-section');
    const bookTitle = document.getElementById('book-title');
    const bookAuthor = document.getElementById('book-author');
    const bookDescription = document.getElementById('book-description');
    const readBookButton = document.getElementById('read-book-button');
    const bookText = document.getElementById('book-text');
    const prevBlockButton = document.getElementById('prev-block-button');
    const nextBlockButton = document.getElementById('next-block-button');
    const showQuestionsButton = document.getElementById('show-questions-button');
    const questionsSection = document.getElementById('questions-section');
    const questionsContainer = document.getElementById('questions-container');
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const backButton = document.getElementById('back-button');
    const readingSection = document.getElementById('reading-section'); // Добавьте эту строку

    let currentUser = null;
    let currentBook = null;
    let currentBlock = 0;

    // Login function
    loginButton.addEventListener('click', function() {
        const login = loginInput.value;
        fetch('/get_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ login })
        })
        .then(response => response.json())
        .then(data => {
            currentUser = data.id_user;
            displayBookList(data);
        })
        .catch(error => console.error('Error:', error));
    });

    // Display book list
    function displayBookList(data) {
        bookListSection.innerHTML = '';
        for (let i = 0; i < data.count_book; i++) {
            const li = document.createElement('li');
            li.textContent = `${data.titles[i]} by ${data.authors[i]} - ${data.status[i]}`;
            li.dataset.id = data.id_books[i];
            li.dataset.title = data.titles[i];
            li.dataset.author = data.authors[i];
            li.dataset.description = data.descriptions[i];
            bookListSection.appendChild(li);
        }
        document.querySelector('body').style.display = 'block';
    }

    // Book list click event
    bookListSection.addEventListener('click', function(event) {
        if (event.target.tagName === 'LI') {
            const bookId = event.target.dataset.id;
            fetch('/get_book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id_user: currentUser, id_book: bookId })
            })
            .then(response => response.json())
            .then(data => {
                displayBookDetail(data);
            })
            .catch(error => console.error('Error:', error));
        }
    });

    // Display book detail
    function displayBookDetail(book) {
        bookDetailSection.style.display = 'block';
        bookListSection.style.display = 'none';
        bookTitle.textContent = book.title;
        bookAuthor.textContent = book.author;
        bookDescription.textContent = book.description;
        currentBook = book.book_id;
        console.log('Current Book ID:', currentBook);
    }

    // Обработчик кнопки "Read Book"
    readBookButton.addEventListener('click', function() {
        // Устанавливаем режим перед получением текста
        fetch('/change_mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_user: currentUser, id_book: currentBook, mode: 'summarization' })
        })
        .then(response => response.json())
        .then(() => {
            // Теперь получаем текст книги
            fetch('/get_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id_user: currentUser, id_book: currentBook })
            })
            .then(response => response.json())
            .then(data => {
                displayBookText(data);
            })
            .catch(error => console.error('Error:', error));
        })
        .catch(error => console.error('Error:', error));
    });

    // Display book text
    function displayBookText(data) {
        bookDetailSection.style.display = 'none';
        readingSection.style.display = 'block';
        bookText.textContent = data.text;
        currentBlock = data.id_block;
    }

    // Previous block button click
    prevBlockButton.addEventListener('click', function() {
        fetch('/back_block_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_user: currentUser, id_book: currentBook })
        })
        .then(() => {
            readBookButton.click();
        })
        .catch(error => console.error('Error:', error));
    });

    // Next block button click
    nextBlockButton.addEventListener('click', function() {
        fetch('/next_block_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_user: currentUser, id_book: currentBook })
        })
        .then(() => {
            readBookButton.click();
        })
        .catch(error => console.error('Error:', error));
    });

    // Show questions button click
    showQuestionsButton.addEventListener('click', function() {
        fetch('/get_questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id_user: currentUser, id_book: currentBook, id_block: currentBlock })
        })
        .then(response => response.json())
        .then(data => {
            displayQuestions(data);
        })
        .catch(error => console.error('Error:', error));
    });

    // Display questions
    function displayQuestions(data) {
        questionsSection.style.display = 'block';
        questionsContainer.innerHTML = '';
        data.questions.forEach((question, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.classList.add('question');
            const questionTitle = document.createElement('h3');
            questionTitle.textContent = `Question ${index + 1}: ${question}`;
            questionDiv.appendChild(questionTitle);
            const answersList = document.createElement('ul');
            data.right_answers[index].forEach(answer => {
                const li = document.createElement('li');
                li.textContent = answer;
                answersList.appendChild(li);
            });
            questionDiv.appendChild(answersList);
            questionsContainer.appendChild(questionDiv);
        });
    }

    // Back button click event
    backButton.addEventListener('click', function() {
        if (bookDetailSection.style.display === 'block') {
            bookDetailSection.style.display = 'none';
            bookListSection.style.display = 'block';
        } else if (readingSection.style.display === 'block') {
            readingSection.style.display = 'none';
            bookDetailSection.style.display = 'block';
        } else if (questionsSection.style.display === 'block') {
            questionsSection.style.display = 'none';
            readingSection.style.display = 'block';
        }
    });

    // Upload book button click
    uploadButton.addEventListener('click', function() {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('id_user', currentUser);

            fetch('/upload_book', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                // После успешной загрузки книги обновляем список книг
                fetch('/get_user', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ login: loginInput.value })
                })
                .then(response => response.json())
                .then(data => {
                    displayBookList(data); // Обновляем список книг
                })
                .catch(error => console.error('Error:', error));
            })
            .catch(error => console.error('Error:', error));
        } else {
            alert('Please select a file first');
        }
    });
});
