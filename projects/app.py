from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

# Create the database and the tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    expenses = Expense.query.all()
    total_expenses = sum(expense.amount for expense in expenses)
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']

    # Add the new expense to the database
    new_expense = Expense(description=description, amount=amount, category=category)
    db.session.add(new_expense)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/charts')
def charts():
    # Prepare data for the chart (grouped by category)
    expense_data = Expense.query.with_entities(Expense.category, db.func.sum(Expense.amount)).group_by(Expense.category).all()
    expense_data_dict = [{'category': category, 'amount': amount} for category, amount in expense_data]
    return render_template('charts.html', expense_data=expense_data_dict)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    # Find the expense by ID
    expense_to_delete = Expense.query.get_or_404(expense_id)
    
    try:
        # Delete the expense from the database
        db.session.delete(expense_to_delete)
        db.session.commit()
        return redirect(url_for('index'))
    except:
        return 'There was a problem deleting that expense'
