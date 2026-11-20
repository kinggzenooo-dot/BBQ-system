
<?php
session_start();

require_once "config/database.php";

$error = "";

if ($_SERVER["REQUEST_METHOD"] === "POST") {

    $email = trim($_POST["email"] ?? "");
    $password = $_POST["password"] ?? "";

    if (empty($email) || empty($password)) {

        $error = "Please enter your email and password.";

    } else {

        $sql = "SELECT id, name, email, password, role
                FROM users
                WHERE email = ?
                LIMIT 1";

        $stmt = $conn->prepare($sql);

        if ($stmt) {

            $stmt->bind_param("s", $email);
            $stmt->execute();

            $result = $stmt->get_result();

            if ($result->num_rows === 1) {

                $user = $result->fetch_assoc();

                /*
                 * Passwords should be stored using password_hash()
                 */
                if (password_verify($password, $user["password"])) {

                    // Prevent session fixation
                    session_regenerate_id(true);

                    $_SESSION["user_id"] = $user["id"];
                    $_SESSION["name"] = $user["name"];
                    $_SESSION["email"] = $user["email"];
                    $_SESSION["role"] = $user["role"];

                    // Redirect based on account type
                    if ($user["role"] === "admin") {

                        header("Location: admin/dashboard.php");
                        exit;

                    } else {

                        header("Location: index.php");
                        exit;
                    }

                } else {

                    $error = "Incorrect email or password.";
                }

            } else {

                $error = "Incorrect email or password.";
            }

            $stmt->close();

        } else {

            $error = "Something went wrong. Please try again.";
        }
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>Login | BBQ House</title>

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
        }

        .login-container {
            width: 100%;
            max-width: 430px;
            padding: 20px;
        }

        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 35px rgba(0,0,0,0.3);
        }

        .logo {
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: #d35400;
            margin-bottom: 10px;
        }

        .login-title {
            text-align: center;
            font-size: 28px;
            margin-bottom: 8px;
            color: #222;
        }

        .login-subtitle {
            text-align: center;
            color: #777;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #333;
        }

        .form-group input {
            width: 100%;
            padding: 13px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 15px;
            outline: none;
        }

        .form-group input:focus {
            border-color: #d35400;
        }

        .login-button {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 8px;
            background: #d35400;
            color: white;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        .login-button:hover {
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

        .register-link {
            text-align: center;
            margin-top: 25px;
            color: #666;
        }

        .register-link a {
            color: #d35400;
            font-weight: bold;
            text-decoration: none;
        }

        .back-home {
            text-align: center;
            margin-top: 20px;
        }

        .back-home a {
            color: #777;
            text-decoration: none;
        }

        .back-home a:hover {
            color: #d35400;
        }

    </style>

</head>

<body>

<div class="login-container">

    <div class="login-box">

        <div class="logo">
            🔥 BBQ HOUSE
        </div>

        <h1 class="login-title">
            Welcome Back
        </h1>

        <p class="login-subtitle">
            Login to your BBQ House account
        </p>


        <?php if (!empty($error)): ?>

            <div class="error">
                <?php echo htmlspecialchars($error); ?>
            </div>

        <?php endif; ?>


        <form method="POST"
              action="login.php">

            <div class="form-group">

                <label for="email">
                    Email Address
                </label>

                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="Enter your email"
                    required
                    value="<?php echo htmlspecialchars($_POST["email"] ?? ""); ?>"
                >

            </div>


            <div class="form-group">

                <label for="password">
                    Password
                </label>

                <input
                    type="password"
                    id="password"
                    name="password"
                    placeholder="Enter your password"
                    required
                >

            </div>


            <button
                type="submit"
                class="login-button">

                Login

            </button>

        </form>


        <div class="register-link">

            Don't have an account?

            <a href="register.php">
                Create Account
            </a>

        </div>


        <div class="back-home">

            <a href="index.php">
                ← Back to Home
            </a>

        </div>

    </div>

</div>

</body>

</html>
```

### `logout.php`

:::writing{variant="document" id="92547" title="BBQ Online Store — logout.php"}
```php
<?php

session_start();

// Remove all session variables
$_SESSION = [];

// Delete the session cookie
if (ini_get("session.use_cookies")) {

    $params = session_get_cookie_params();

    setcookie(
        session_name(),
        '',
        time() - 42000,
        $params["path"],
        $params["domain"],
        $params["secure"],
        $params["httponly"]
    );
}

// Destroy the session
session_destroy();

// Return to login page
header("Location: login.php");
exit;

?>