import csv

from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Gratitude(db.Model):
    # Sets the ID
    id = db.Column(db.Integer, primary_key=True)

    # To write the gratitude entries
    content = db.Column(db.String(250), nullable=False)

    # Records the date the entry was made
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Makes it easier to debug
    def __repr__(self):
        return f'<Gratitude {self.id}>'


# Displays all the gratitude entries on the Home Page
@app.route('/')
def index():
    # Gets all entries
    entries = Gratitude.query.order_by(Gratitude.date_created).all()

    # Gets the total number of entries
    total_entries = Gratitude.query.count()

    # Displays the entries using an HTML Template
    return render_template('index.html', entries=entries, total_entries=total_entries)


# To add a new Gratitude Entry
@app.route('/add', methods=['POST'])
def add_gratitude():
    content = request.form['content']
    new_entry = Gratitude(content=content)

    try:
        db.session.add(new_entry)  # Takes the new entry
        db.session.commit()  # Saves changes
        return redirect('/')  # Refreshes page with the new entry

    except Exception as e:
        return f'There was an issue adding the entry: {e}'


# To delete a Gratitude Entry
@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete = Gratitude.query.get_or_404(id)

    try:
        db.session.delete(entry_to_delete)  # Takes the entry to delete
        db.session.commit()  # Commits this delete to the database
        return redirect('/')  # Refeshes page with the new changes

    except:
        return 'There was a problem deleting that entry'


# To update a Gratitude Entry
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    entry = Gratitude.query.get_or_404(id)

    # If asked to send data, content is reassigned new value
    if request.method == 'POST':
        entry.content = request.form['content']

        try:
            db.session.commit()  # Commits the changes made
            return redirect('/')  # Refreshes page with new changes

        except:
            # if no changes were made
            return 'There was an issue with the updating'

    else:
        return render_template('update.html', entry=entry)


# Search Feature
'''@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']  # Takes the query that the user searched for

    # Checks if any matches exist in the Gratitude content
    entries = Gratitude.query.filter(
        Gratitude.content.like(f'%{query}%')).all()

   # Displays the matches on the 'index.html' page
    return render_template('index.html', entries=entries)'''


# Export the data to a CSV


@app.route('/export')
def export():
    entries = Gratitude.query.all()

    with open('gratitude_entries.csv', 'w', newline='') as csvfile:
        fieldnames = ['Content', 'Date Created']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for entry in entries:
            writer.writerow({'Content': entry.content,
                            'Date Created': entry.date_created})

    return send_file('gratitude_entries.csv', as_attachment=True)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # This will create the 'Gratitude' table in the database
    app.run(debug=True)
