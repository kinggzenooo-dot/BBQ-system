
<?php
session_start();

require_once "config/database.php";

$error = "";
$success = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {

    $name = trim($_POST["name"] ?? "");
    $email = trim($_POST["email"] ?? "");
    $phone = trim($_POST["phone"] ?? "");
    $address = trim($_POST["address"] ?? "");
    $password = $_POST["password"] ?? "";
    $confirmPassword = $_POST["confirm_password"] ?? "";
    $role = $_POST["role"] ?? "customer";

    // -----------------------------
    // VALIDATION
    // -----------------------------

    if (
        empty($name) ||
        empty($email) ||
        empty($password) ||
        empty($confirmPassword) ||
        empty($role)
    ) {

        $error = "Please fill in all required fields.";

    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {

        $error = "Please enter a valid email address.";

    } elseif (strlen($password) < 6) {

        $error = "Password must be at least 6 characters.";

    } elseif ($password !== $confirmPassword) {

        $error = "Passwords do not match.";

    } elseif (!in_array($role, ["customer", "admin"])) {

        $error = "Invalid account type.";

    } else {

        // -----------------------------
        // CHECK IF EMAIL EXISTS
        // -----------------------------

        $checkSql = "SELECT id FROM users WHERE email = ? LIMIT 1";

        $checkStmt = $conn->prepare($checkSql);

        if ($checkStmt) {

            $checkStmt->bind_param("s", $email);
            $checkStmt->execute();

            $checkResult = $checkStmt->get_result();

            if ($checkResult->num_rows > 0) {

                $error = "An account with this email already exists.";

            } else {

                // -----------------------------
                // HASH PASSWORD
                // -----------------------------

                $hashedPassword = password_hash(
                    $password,
                    PASSWORD_DEFAULT
                );

                // -----------------------------
                // INSERT USER
                // -----------------------------

                $sql = "INSERT INTO users
                        (name, email, password, role, phone, address)
                        VALUES (?, ?, ?, ?, ?, ?)";

                $stmt = $conn->prepare($sql);

                if ($stmt) {

                    $stmt->bind_param(
                        "ssssss",
                        $name,
                        $email,
                        $hashedPassword,
                        $role,
                        $phone,
                        $address
                    );

                    if ($stmt->execute()) {

                        $success = "Account created successfully!";

                        // Clear form values
                        $_POST = [];

                    } else {

                        $error = "Registration failed. Please try again.";
                    }

                    $stmt->close();

                } else {

                    $error = "Database error. Please try again.";
                }
            }

            $checkStmt->close();

        } else {

            $error = "Database error. Please try again.";
        }
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Create Account | BBQ House</title>

    <link rel="stylesheet" href="css/style.css">

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;

            min-height: 100vh;

            background:
                linear-gradient(
                    rgba(0, 0, 0, 0.65),
                    rgba(0, 0, 0, 0.65)
                ),
                url("images/banner.jpg");

            background-size: cover;
            background-position: center;

            display: flex;
            align-items: center;
            justify-content: center;

            padding: 30px 15px;
        }

        .register-container {
            width: 100%;
            max-width: 500px;
        }

        .register-box {
            background: #ffffff;

            padding: 40px;

            border-radius: 15px;

            box-shadow:
                0 10px 35px rgba(0, 0, 0, 0.3);
        }

        .logo {
            text-align: center;

            font-size: 28px;

            font-weight: bold;

            color: #d35400;

            margin-bottom: 10px;
        }

        .register-title {
            text-align: center;

            font-size: 28px;

            color: #222;

            margin-bottom: 8px;
        }

        .register-subtitle {
            text-align: center;

            color: #777;

            margin-bottom: 25px;
        }

        .form-group {
            margin-bottom: 17px;
        }

        .form-group label {
            display: block;

            margin-bottom: 7px;

            font-weight: bold;

            color: #333;
        }

        .required {
            color: #e74c3c;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {

            width: 100%;

            padding: 12px;

            border: 1px solid #ddd;

            border-radius: 8px;

            font-size: 15px;

            outline: none;

            font-family: Arial, sans-serif;
        }

        .form-group textarea {

            height: 80px;

            resize: vertical;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {

            border-color: #d35400;

            box-shadow:
                0 0 0 2px rgba(211, 84, 0, 0.1);
        }

        .account-type {

            display: grid;

            grid-template-columns: 1fr 1fr;

            gap: 10px;

            margin-top: 5px;
        }

        .account-option {

            border: 1px solid #ddd;

            border-radius: 8px;

            padding: 12px;

            cursor: pointer;

            text-align: center;

            transition: 0.2s;
        }

        .account-option:hover {

            border-color: #d35400;

            background: #fff7f0;
        }

        .account-option input {

            margin-right: 5px;

            accent-color: #d35400;
        }

        .register-button {

            width: 100%;

            padding: 14px;

            border: none;

            border-radius: 8px;

            background: #d35400;

            color: white;

            font-size: 16px;

            font-weight: bold;

            cursor: pointer;

            margin-top: 5px;
        }

        .register-button:hover {

            background: #a04000;
        }

        .error {

            background: #ffe6e6;

            color: #c0392b;

            padding: 12px;

            border-radius: 8px;

            margin-bottom: 20px;

            text-align: center;
        }

        .success {

            background: #e8f8ef;

            color: #218c54;

            padding: 12px;

            border-radius: 8px;

            margin-bottom: 20px;

            text-align: center;
        }

        .login-link {

            text-align: center;

            margin-top: 22px;

            color: #666;
        }

        .login-link a {

            color: #d35400;

            font-weight: bold;

            text-decoration: none;
        }

        .back-home {

            text-align: center;

            margin-top: 18px;
        }

        .back-home a {

            color: #777;

            text-decoration: none;
        }

        .back-home a:hover {

            color: #d35400;
        }

        .note {

            font-size: 12px;

            color: #888;

            margin-top: 6px;
        }

        @media (max-width: 500px) {

            .register-box {
                padding: 25px 20px;
            }

            .account-type {
                grid-template-columns: 1fr;
            }

        }

    </style>

</head>

<body>

<div class="register-container">

    <div class="register-box">

        <div class="logo">
            🔥 BBQ HOUSE
        </div>

        <h1 class="register-title">
            Create Account
        </h1>

        <p class="register-subtitle">
            Join BBQ House and start ordering!
        </p>


        <!-- ERROR MESSAGE -->

        <?php if (!empty($error)): ?>

            <div class="error">

                <?php echo htmlspecialchars($error); ?>

            </div>

        <?php endif; ?>


        <!-- SUCCESS MESSAGE -->

        <?php if (!empty($success)): ?>

            <div class="success">

                <?php echo htmlspecialchars($success); ?>

                <br><br>

                <a href="login.php">
                    Click here to login
                </a>

            </div>

        <?php endif; ?>


        <!-- REGISTRATION FORM -->

        <form
            method="POST"
            action="register.php"
        >

            <!-- NAME -->

            <div class="form-group">

                <label for="name">
                    Full Name
                    <span class="required">*</span>
                </label>

                <input
                    type="text"
                    id="name"
                    name="name"
                    placeholder="Enter your full name"
                    required
                    value="<?php echo htmlspecialchars($_POST["name"] ?? ""); ?>"
                >

            </div>


            <!-- EMAIL -->

            <div class="form-group">

                <label for="email">
                    Email Address
                    <span class="required">*</span>
                </label>

                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="example@email.com"
                    required
                    value="<?php echo htmlspecialchars($_POST["email"] ?? ""); ?>"
                >

            </div>


            <!-- PHONE -->

            <div class="form-group">

                <label for="phone">
                    Phone Number
                </label>

                <input
                    type="text"
                    id="phone"
                    name="phone"
                    placeholder="09XXXXXXXXX"
                    value="<?php echo htmlspecialchars($_POST["phone"] ?? ""); ?>"
                >

            </div>


            <!-- ADDRESS -->

            <div class="form-group">

                <label for="address">
                    Delivery Address
                </label>

                <textarea
                    id="address"
                    name="address"
                    placeholder="Enter your complete delivery address"
                ><?php echo htmlspecialchars($_POST["address"] ?? ""); ?></textarea>

            </div>


            <!-- ACCOUNT TYPE -->

            <div class="form-group">

                <label>
                    Account Type
                    <span class="required">*</span>
                </label>

                <div class="account-type">

                    <label class="account-option">

                        <input
                            type="radio"
                            name="role"
                            value="customer"
                            <?php
                            if (
                                ($_POST["role"] ?? "customer")
                                === "customer"
                            ) {
                                echo "checked";
                            }
                            ?>
                        >

                        👤 Customer

                    </label>


                    <label class="account-option">

                        <input
                            type="radio"
                            name="role"
                            value="admin"
                            <?php
                            if (
                                ($_POST["role"] ?? "")
                                === "admin"
                            ) {
                                echo "checked";
                            }
                            ?>
                        >

                        👨‍💼 Admin

                    </label>

                </div>

                <p class="note">
                    Select the account type you want to create.
                </p>

            </div>


            <!-- PASSWORD -->

            <div class="form-group">

                <label for="password">

                    Password
                    <span class="required">*</span>

                </label>

                <input
                    type="password"
                    id="password"
                    name="password"
                    placeholder="At least 6 characters"
                    required
                >

            </div>


            <!-- CONFIRM PASSWORD -->

            <div class="form-group">

                <label for="confirm_password">

                    Confirm Password
                    <span class="required">*</span>

                </label>

                <input
                    type="password"
                    id="confirm_password"
                    name="confirm_password"
                    placeholder="Re-enter your password"
                    required
                >

            </div>


            <!-- REGISTER BUTTON -->

            <button
                type="submit"
                class="register-button"
            >

                Create Account

            </button>

        </form>


        <!-- LOGIN -->

        <div class="login-link">

            Already have an account?

            <a href="login.php">
                Login
            </a>

        </div>


        <!-- HOME -->

        <div class="back-home">

            <a href="index.php">
                ← Back to Home
            </a>

        </div>

    </div>

</div>

</body>

</html>