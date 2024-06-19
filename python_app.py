# python_app.py

!pip install flask-ngrok pandas pyngrok

import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from pyngrok import ngrok

# Flask app initialization
app = Flask(__name__)
app.static_folder = 'static'

# --- Ngrok Setup for Public Accessibility ---
ngrok.set_auth_token("YOUR_ACTUAL_TOKEN_FROM_NGROK")  # Replace with your actual token
public_url = ngrok.connect(addr="5000")  # Create a tunnel to port 5000 (default for Flask)
print(f" * Running on {public_url}")  # Print the public URL provided by ngrok

# --- Data Loading and Preparation ---
df = pd.read_csv('PUT YOUR FILE PATH HERE!!!')  # Update the path to your CSV file
df.columns = df.columns.str.strip()  # Clean column names (remove leading/trailing spaces)

# Convert price and stars columns to numeric
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['stars'] = pd.to_numeric(df['stars'], errors='coerce')

# Ensure isBestSeller column is boolean and handle NaN values
df['isBestSeller'] = df['isBestSeller'].fillna('No')

# Create a new column for price range
def categorize_price(price):
    if price <= 20:
        return 1
    elif 20 < price <= 50:
        return 2
    elif 50 < price <= 100:
        return 3
    else:
        return 4

df['price_range'] = df['price'].apply(categorize_price)

# Sort the categories and price ranges
categories = sorted(df['categoryName'].unique())

# --- HTML Template for User Interface ---
html_template = """
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Guru</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            display: flex;
            flex-direction: column;
            height: 100vh;
            margin: 0;
        }

        .main-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .form-container {
            flex: 0 0 300px;
            padding: 20px;
            background-color: #f8f9fa;
            overflow-y: auto;
        }

        .results-container {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        .footer {
            text-align: center;
            padding: 10px;
            background-color: #000;
            color: white;
            flex-shrink: 0;
        }

        h1 {
            text-align: center;
        }

        .card img {
            max-width: 100%;
            height: auto;
        }
    </style>
</head>

<body>
    <div class="main-container">
        <div class="form-container">
            <h2>Filter Options</h2>
            <form id="suggestion-form">
                <div class="mb-3">
                    <label for="stars" class="form-label">Stars</label>
                    <div class="row">
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="0" id="stars0" name="stars">
                                <label class="form-check-label" for="stars0">0 Stars</label>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="1" id="stars1" name="stars">
                                <label class="form-check-label" for="stars1">1 Star</label>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="2" id="stars2" name="stars">
                                <label class="form-check-label" for="stars2">2 Stars</label>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="3" id="stars3" name="stars">
                                <label class="form-check-label" for="stars3">3 Stars</label>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="4" id="stars4" name="stars">
                                <label class="form-check-label" for="stars4">4 Stars</label>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" value="5" id="stars5" name="stars">
                                <label class="form-check-label" for="stars5">5 Stars</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">Category</label>
                    <select class="form-select" id="category" name="category" required>
                        <!-- Options dynamically populated -->
                    </select>
                </div>
                <div class="mb-3">
                    <label for="price_range" class="form-label">Price Range</label>
                    <select class="form-select" id="price_range" name="price_range" required>
                        <option value="1">$20 or Under</option>
                        <option value="2">$20 - $50</option>
                        <option value="3">$50 - $100</option>
                        <option value="4">$100 and Over</option>
                    </select>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="is_best_seller" name="is_best_seller">
                        <label class="form-check-label" for="is_best_seller">Best Sellers Only</label>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">Product Suggestion</button>
            </form>
        </div>
        <div class="results-container">
            <h1 class="mb-4">Product Guru</h1>
            <div id="result" class="mt-4"></div>
        </div>
    </div>
    <div class="footer">
        <p>Made by Victor Costa</p>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $(document).ready(function () {
            // Fetch categories and populate the select dropdown
            $.ajax({
                url: '/categories',  // This endpoint should return the list of categories
                method: 'GET',
                success: function (data) {
                    let categorySelect = $('#category');
                    data.categories.forEach(category => {
                        categorySelect.append(new Option(category, category));
                    });
                },
                error: function (jqXHR) {
                    console.error('Error fetching categories:', jqXHR.responseText);
                }
            });

            $('#suggestion-form').on('submit', function (e) {
                e.preventDefault();

                $.ajax({
                    url: '/suggest',
                    method: 'POST',
                    data: $(this).serialize(),
                    beforeSend: function (xhr) {
                        xhr.setRequestHeader('ngrok-skip-browser-warning', 'true'); // Or any value
                    },
                    success: function (data) {
                        if (data.error) {
                            $('#result').html('<div class="alert alert-warning">' + data.error + '</div>');
                        } else {
                            let resultHtml = '<h3>Suggested Products</h3>';
                            data.forEach(product => {
                                resultHtml += `
                                    <div class="card mb-3">
                                        <div class="row g-0">
                                            <div class="col-md-4">
                                                <img src="${product.imgUrl}" class="img-fluid rounded-start" alt="${product.title}">
                                            </div>
                                            <div class="col-md-8">
                                                <div class="card-body">
                                                    <p><strong>SKU:</strong> ${product.asin}</p>
                                                    <p><strong>Title:</strong> ${product.title}</p>
                                                    <p><strong>Stars:</strong> ${product.stars}</p>
                                                    <p><strong>Reviews:</strong> ${product.reviews}</p>
                                                    <p><strong>Price:</strong> $${product.price.toFixed(2)}</p>
                                                    <p><strong>Category:</strong> ${product.categoryName}</p>
                                                    <p><strong>Bought in Last Month:</strong> ${product.boughtInLastMonth}</p>
                                                    <a href="${product.productURL}" target="_blank" class="btn btn-primary">View Product</a>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            });
                            $('#result').html(resultHtml);
                        }
                        $('html, body').animate({ scrollTop: 0 }, 'fast');
                    },
                    error: function (jqXHR) {
                        $('#result').html('<div class="alert alert-danger">Error: ' + jqXHR.responseText + '</div>');
                        $('html, body').animate({ scrollTop: 0 }, 'fast');
                    }
                });
            });
        });
    </script>
</body>

</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template_string(html_template, categories=categories)

@app.route('/categories', methods=['GET'])
def get_categories():
    return jsonify({"categories": categories})

@app.route('/suggest', methods=['POST'])
def suggest():
    """Handles the form submission, filters the DataFrame, and returns matching products as JSON."""

    # Get form data
    selected_stars = request.form.getlist('stars')
    category = request.form.get('category')
    price_range = int(request.form.get('price_range'))
    is_best_seller = 'is_best_seller' in request.form  # Check if the checkbox is selected

    # Filter by stars
    if selected_stars:
        stars_filter = df['stars'].apply(lambda x: any(
            (int(star) == 0 and x == 0) or
            (int(star) == 1 and 0 < x <= 1) or
            (int(star) == 2 and 1 < x <= 2) or
            (int(star) == 3 and 2 < x <= 3) or
            (int(star) == 4 and 3 < x <= 4) or
            (int(star) == 5 and 4 < x <= 5) for star in selected_stars
        ))
    else:
        stars_filter = df['stars'] >= 0  # If no stars selected, select all

    filtered_stars_df = df[stars_filter]
    filtered_category_df = filtered_stars_df[filtered_stars_df['categoryName'] == category]
    filtered_price_df = filtered_category_df[filtered_category_df['price_range'] == price_range]

    if is_best_seller:
        filtered_df = filtered_price_df[filtered_price_df['isBestSeller'] == True]
    else:
        filtered_df = filtered_price_df  # Include all when the checkbox is not selected

    filtered_df = filtered_df.sort_values(by='title')

    if not filtered_df.empty:
        products = filtered_df.nlargest(10, 'stars').to_dict(orient='records')
        return jsonify(products)
    else:
        relaxed_price_range = price_range + 1 if price_range < 4 else 1  # Expand to the next range (loop back to 1 if at 4)
        fallback_df = filtered_category_df[filtered_category_df['price_range'] <= relaxed_price_range]

        if not fallback_df.empty:
            fallback_df = fallback_df.sort_values(by='title')
            products = fallback_df.nlargest(10, 'stars').to_dict(orient='records')
            return jsonify({"suggestions": products, "message": "No exact matches, showing similar products."})
        else:
            return jsonify({"error": "No products found even with broader criteria."})

if __name__ == '__main__':
    app.run()  # Run the Flask app
