import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# A secret key is required for flashing messages.
app.config['SECRET_KEY'] = 'your_super_secret_key_for_flash_messages'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Book(db.Model):
    """Represents a book in the library's inventory."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'

# --- Routes ---

@app.route('/')
def index():
    """Main page, displays all books, ordered by title."""
    books = db.session.execute(db.select(Book).order_by(Book.title)).scalars()
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    """Handles adding a new book to the database via a form."""
    if request.method == 'POST':
        # Get data from the submitted form
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])

        # Create a new book instance
        new_book = Book(title=title, author=author, isbn=isbn, price=price, quantity=quantity)

        # Add the new book to the database session and commit
        db.session.add(new_book)
        db.session.commit()

        flash(f'Book "{title}" has been added successfully!', 'success')
        return redirect(url_for('index'))

    # If GET request, just display the form
    return render_template('book_form.html', title="Add a New Book")

@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    """Handles editing an existing book."""
    book = db.get_or_404(Book, book_id)

    if request.method == 'POST':
        # Update book attributes from the form data
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.price = float(request.form['price'])
        book.quantity = int(request.form['quantity'])

        db.session.commit()

        flash(f'Book "{book.title}" has been updated successfully!', 'success')
        return redirect(url_for('index'))

    # If GET request, display the form with the book's current data
    return render_template('book_form.html', title="Edit Book", book=book)

@app.route('/sell/<int:book_id>', methods=['POST'])
def sell_book(book_id):
    """Decrements the quantity of a book by one."""
    book = db.get_or_404(Book, book_id)

    if book.quantity > 0:
        book.quantity -= 1
        db.session.commit()
        flash(f'One copy of "{book.title}" has been sold.', 'success')
    else:
        flash(f'Cannot sell "{book.title}", it is out of stock.', 'danger')

    return redirect(url_for('index'))

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """Deletes a book from the database."""
    book = db.get_or_404(Book, book_id)
    title = book.title

    db.session.delete(book)
    db.session.commit()

    flash(f'Book "{title}" has been deleted.', 'success')
    return redirect(url_for('index'))


# --- CLI Command to create the database ---
@app.cli.command('create-db')
def create_db():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    print('Database created!')
