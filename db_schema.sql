-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 06, 2025 at 10:49 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ecofinds`
--

-- --------------------------------------------------------

--
-- Table structure for table `auths`
--

CREATE TABLE `auths` (
  `user_id` int(11) NOT NULL,
  `token` varchar(512) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `expires_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auths`
--

INSERT INTO `auths` (`user_id`, `token`, `created_at`, `expires_at`) VALUES
(1, '1112ca20a7de58e23016fae5f1a18b57d126a181792add56de35cac6ff91d9e1', '2025-09-06 06:44:04', NULL),
(1, '39cc15453febe57e84315cb8b9e6def3c158140f9d122912c15be1569eb09c62', '2025-09-06 07:27:39', NULL),
(1, 'a053db2d2d0cb172ce41ce81c7c73830c7bd7df9a3f559353094a36607134d49', '2025-09-06 07:32:13', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `cart_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `total_price` decimal(10,2) DEFAULT NULL,
  `added_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `category` enum('Electronics','Furniture','Clothing','Books','Others') NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `item_condition` enum('New','Like New','Used','For Parts') NOT NULL,
  `year_of_manufacture` year(4) DEFAULT NULL,
  `brand` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `length` decimal(10,2) DEFAULT NULL,
  `width` decimal(10,2) DEFAULT NULL,
  `height` decimal(10,2) DEFAULT NULL,
  `weight` decimal(10,2) DEFAULT NULL,
  `material` varchar(100) DEFAULT NULL,
  `color` varchar(50) DEFAULT NULL,
  `original_packaging` tinyint(1) DEFAULT 0,
  `manual_included` tinyint(1) DEFAULT 0,
  `working_condition` text DEFAULT NULL,
  `product_image` varchar(255) DEFAULT NULL,
  `product_image_2` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `user_id`, `title`, `description`, `category`, `price`, `quantity`, `item_condition`, `year_of_manufacture`, `brand`, `model`, `length`, `width`, `height`, `weight`, `material`, `color`, `original_packaging`, `manual_included`, `working_condition`, `product_image`, `product_image_2`, `created_at`) VALUES
(1, 1, 'shoes', 'High performance shoes', 'Clothing', 50000.00, 1, 'Like New', NULL, 'PUMA', 'XPS 13', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, 'uploads/products/shoes.jpg', 'uploads/products/sports_shoes.jpg', '2025-09-06 06:53:24'),
(2, 2, 'Chair', 'Comfortable office chair', 'Furniture', 2000.00, 3, 'Used', NULL, 'Ikea', 'Markus', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, 'uploads/products/chair.jpg', 'uploads/products/chair.jpg', '2025-09-06 06:53:24'),
(3, 1, 'T-Shirt', 'Cotton casual t-shirt', 'Clothing', 500.00, 10, 'New', NULL, 'Polo', 'Casual Fit', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, 'uploads/products/chair.jpg', 'uploads/products/chair.jpg', '2025-09-06 06:53:24'),
(4, 2, 'Book', 'Data Structures textbook', 'Books', 300.00, 5, 'Like New', NULL, 'Pearson', 'DSA 2nd Edition', NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, NULL, 'uploads/products/book_dsa.jpeg', 'uploads/products/book_dsa.jpeg', '2025-09-06 06:53:24');

-- --------------------------------------------------------

--
-- Table structure for table `product_purchase_history`
--

CREATE TABLE `product_purchase_history` (
  `purchase_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `total_price` decimal(10,2) NOT NULL,
  `purchased_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `contact_no` varchar(20) DEFAULT NULL,
  `profile_pic` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `username` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password_hash`, `contact_no`, `profile_pic`, `created_at`, `username`) VALUES
(1, 'shivang', 'abc@gmail.com', 'scrypt:32768:8:1$IXPZpds7YwWDvuOA$1c03506d2dab4733778b08f286ccc5965f1cda625ff5f683e3d25856f26edd525ffbfb08ce9a3b67dea0ab22d84c88eef847c9ff8fbe00f74af389957de5b7e5', '123456789', '/static/uploads/profile_pics/user_1.jpg', '2025-09-06 06:43:37', 'shivang'),
(2, 'prkr', 'test2@gmail.com', 'scrypt:32768:8:1$5HcJ2LzJsMlyqEqn$ad88db5f91e7d9d881b6d8bae03d6ce41e53f34fbf026a0b5f305d9fa4798fc39e1a6d3ae758e5c6e3bf21836e46828c6d9719795b5b74b3705d5ba06d7700e8', NULL, NULL, '2025-09-06 06:48:47', 'prkr');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auths`
--
ALTER TABLE `auths`
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`cart_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `product_purchase_history`
--
ALTER TABLE `product_purchase_history`
  ADD PRIMARY KEY (`purchase_id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `cart_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `product_purchase_history`
--
ALTER TABLE `product_purchase_history`
  MODIFY `purchase_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auths`
--
ALTER TABLE `auths`
  ADD CONSTRAINT `auths_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `product_purchase_history`
--
ALTER TABLE `product_purchase_history`
  ADD CONSTRAINT `purchase_product_fk` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `purchase_user_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
