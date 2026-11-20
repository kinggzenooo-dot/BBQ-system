<?php
session_start();

// Check if user is logged in
$isLoggedIn = isset($_SESSION['user_id']);
$userName = $_SESSION['name'] ?? '';

/*
|--------------------------------------------------------------------------
| Featured Products
|--------------------------------------------------------------------------
| These are temporary sample products.
| Later, we can load them from the MySQL products table.
*/

$featuredProducts = [
    [
        'name' => 'Classic Pork BBQ',
        'description' => 'Tender and juicy marinated pork BBQ skewers.',
        'price' => 35.00,
        'image' => 'images/products/pork-bbq.jpg'
    ],
    [
        'name' => 'Chicken BBQ',
        'description' => 'Delicious grilled chicken with our special BBQ sauce.',
        'price' => 40.00,
        'image' => 'images/products/chicken-bbq.jpg'
    ],
    [
        'name' => 'BBQ Meal',
        'description' => 'BBQ served with rice and our signature sauce.',
        'price' => 99.00,
        'image' => 'images/products/bbq-meal.jpg'
    ]
];
?>

<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>BBQ House | Online BBQ Store</title>

    <link rel="stylesheet" href="css/style.css">

</head>

<body>


<!-- =====================================================
     NAVIGATION
===================================================== -->

<header class="navbar">

    <div class="nav-container">

        <a href="index.php" class="logo">
            🔥 BBQ HOUSE
        </a>


        <nav class="nav-links">

            <a href="index.php">
                Home
            </a>

            <a href="products.php">
                Menu
            </a>

            <a href="cart.php">
                🛒 Cart
            </a>


            <?php if ($isLoggedIn): ?>

                <a href="my-orders.php">
                    My Orders
                </a>

                <a href="profile.php">
                    <?php echo htmlspecialchars($userName); ?>
                </a>

                <a href="logout.php" class="login-btn">
                    Logout
                </a>


            <?php else: ?>

                <a href="login.php">
                    Login
                </a>

                <a href="register.php" class="login-btn">
                    Sign Up
                </a>

            <?php endif; ?>

        </nav>

    </div>

</header>


<!-- =====================================================
     HERO SECTION
===================================================== -->

<section class="hero">

    <div class="hero-content">


        <div class="hero-text">

            <p class="hero-small">
                🔥 FRESH FROM THE GRILL
            </p>


            <h1>
                Delicious BBQ
                <br>
                <span>Made For You</span>
            </h1>


            <p>
                Enjoy freshly grilled BBQ made with quality
                ingredients, special marinades, and our
                signature sauce.
            </p>


            <div class="hero-buttons">

                <a
                    href="products.php"
                    class="btn-primary"
                >
                    Order Now
                </a>


                <a
                    href="products.php"
                    class="btn-secondary"
                >
                    View Menu
                </a>

            </div>

        </div>


        <div class="hero-image">

            <img
                src="images/banner.jpg"
                alt="Delicious BBQ"
            >

        </div>

    </div>

</section>


<!-- =====================================================
     CATEGORIES
===================================================== -->

<section class="categories">

    <div class="section-title">

        <p>
            WHAT WE SERVE
        </p>

        <h2>
            Our BBQ Categories
        </h2>

        <span>
            Choose your favorite grilled food.
        </span>

    </div>


    <div class="category-container">


        <!-- BBQ MEALS -->

        <a
            href="products.php?category=BBQ%20Meals"
            class="category-card"
        >

            <div class="category-icon">
                🍱
            </div>

            <h3>
                BBQ Meals
            </h3>

            <p>
                Complete BBQ meals with rice.
            </p>

        </a>


        <!-- BBQ SKEWERS -->

        <a
            href="products.php?category=BBQ%20Skewers"
            class="category-card"
        >

            <div class="category-icon">
                🍢
            </div>

            <h3>
                BBQ Skewers
            </h3>

            <p>
                Delicious grilled meat skewers.
            </p>

        </a>


        <!-- CHICKEN BBQ -->

        <a
            href="products.php?category=Chicken%20BBQ"
            class="category-card"
        >

            <div class="category-icon">
                🍗
            </div>

            <h3>
                Chicken BBQ
            </h3>

            <p>
                Tender and flavorful chicken.
            </p>

        </a>


        <!-- PORK BBQ -->

        <a
            href="products.php?category=Pork%20BBQ"
            class="category-card"
        >

            <div class="category-icon">
                🥩
            </div>

            <h3>
                Pork BBQ
            </h3>

            <p>
                Juicy and tasty pork BBQ.
            </p>

        </a>

    </div>

</section>


<!-- =====================================================
     FEATURED PRODUCTS
===================================================== -->

<section class="featured">

    <div class="section-title">

        <p>
            OUR SPECIALS
        </p>

        <h2>
            Popular BBQ
        </h2>

        <span>
            Our customers' favorite grilled dishes.
        </span>

    </div>


    <div class="product-container">


        <?php foreach ($featuredProducts as $product): ?>


            <div class="product-card">


                <!-- PRODUCT IMAGE -->

                <div class="product-image">

                    <img
                        src="<?php echo htmlspecialchars($product['image']); ?>"
                        alt="<?php echo htmlspecialchars($product['name']); ?>"
                    >

                </div>


                <!-- PRODUCT INFORMATION -->

                <div class="product-info">

                    <h3>
                        <?php
                        echo htmlspecialchars($product['name']);
                        ?>
                    </h3>


                    <p>
                        <?php
                        echo htmlspecialchars($product['description']);
                        ?>
                    </p>


                    <div class="product-bottom">


                        <span class="price">

                            ₱<?php
                            echo number_format(
                                $product['price'],
                                2
                            );
                            ?>

                        </span>


                        <a
                            href="products.php"
                            class="order-btn"
                        >
                            Order
                        </a>


                    </div>

                </div>

            </div>


        <?php endforeach; ?>

    </div>


    <div class="view-menu">

        <a
            href="products.php"
            class="btn-primary"
        >
            View Full Menu →
        </a>

    </div>

</section>


<!-- =====================================================
     WHY CHOOSE US
===================================================== -->

<section class="why-us">

    <div class="section-title">

        <p>
            WHY BBQ HOUSE?
        </p>

        <h2>
            Made With Quality
        </h2>

    </div>


    <div class="features">


        <!-- FEATURE 1 -->

        <div class="feature">

            <div class="feature-icon">
                🔥
            </div>

            <h3>
                Freshly Grilled
            </h3>

            <p>
                Our BBQ is grilled fresh for every order.
            </p>

        </div>


        <!-- FEATURE 2 -->

        <div class="feature">

            <div class="feature-icon">
                🥩
            </div>

            <h3>
                Quality Ingredients
            </h3>

            <p>
                We use carefully selected ingredients.
            </p>

        </div>


        <!-- FEATURE 3 -->

        <div class="feature">

            <div class="feature-icon">
                🚴
            </div>

            <h3>
                Fast Delivery
            </h3>

            <p>
                Get your favorite BBQ delivered to your door.
            </p>

        </div>


        <!-- FEATURE 4 -->

        <div class="feature">

            <div class="feature-icon">
                ❤️
            </div>

            <h3>
                Made With Love
            </h3>

            <p>
                Great food prepared with care and passion.
            </p>

        </div>

    </div>

</section>


<!-- =====================================================
     CALL TO ACTION
===================================================== -->

<section class="cta">

    <div class="cta-content">

        <h2>
            Hungry for BBQ?
        </h2>

        <p>
            Order your favorite BBQ today!
        </p>

        <a
            href="products.php"
            class="btn-primary"
        >
            Order Now
        </a>

    </div>

</section>


<!-- =====================================================
     FOOTER
===================================================== -->

<footer class="footer">

    <div class="footer-container">


        <!-- ABOUT -->

        <div class="footer-column">

            <h2>
                🔥 BBQ HOUSE
            </h2>

            <p>
                Delicious BBQ made fresh and served with love.
            </p>

        </div>


        <!-- QUICK LINKS -->

        <div class="footer-column">

            <h3>
                Quick Links
            </h3>

            <a href="index.php">
                Home
            </a>

            <a href="products.php">
                Menu
            </a>

            <a href="cart.php">
                Cart
            </a>

            <a href="my-orders.php">
                My Orders
            </a>

        </div>


        <!-- ACCOUNT -->

        <div class="footer-column">

            <h3>
                Account
            </h3>

            <a href="login.php">
                Login
            </a>

            <a href="register.php">
                Create Account
            </a>

        </div>


        <!-- CONTACT -->

        <div class="footer-column">

            <h3>
                Contact
            </h3>

            <p>
                📞 0912-345-6789
            </p>

            <p>
                📧 bbqhouse@example.com
            </p>

            <p>
                📍 Bohol, Philippines
            </p>

        </div>

    </div>


    <!-- COPYRIGHT -->

    <div class="footer-bottom">

        <p>

            © <?php echo date("Y"); ?>

            BBQ House.

            All Rights Reserved.

        </p>

    </div>

</footer>


</body>

</html>