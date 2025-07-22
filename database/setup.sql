-- MySQL Setup Script for Article Summary Database
-- Run this in MySQL Workbench to create the database and tables

CREATE DATABASE IF NOT EXISTS article_summary_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE article_summary_db;

-- main articles table
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content_hash VARCHAR(32) UNIQUE NOT NULL,
    headline TEXT NOT NULL,
    date DATE,
    article_url TEXT,
    source_url TEXT,
    content_length INT,
    sentence_count INT,
    tech_keyword_count INT,
    quality_score INT,
    sentiment ENUM('利好', '中立', '利弊') NOT NULL,
    summary TEXT NOT NULL,
    relevant ENUM('是', '否') NOT NULL,
    processing_status ENUM('success', 'failed', 'low_quality', 'no_content', 'error') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- indexes for better query performance!
    INDEX idx_date (date),
    INDEX idx_sentiment (sentiment),  #这个是利好/利弊
    INDEX idx_relevant (relevant),  #对这个用户有没有用
    INDEX idx_processing_status (processing_status),   #llm的return成功了还是失败了，失败的话就不要用这个数据
    INDEX idx_quality_score (quality_score),     #原文的质量，0-10，如果低于3我就不会发给llm自动失败
    INDEX idx_created_at (created_at)
);

--quality_factors table
CREATE TABLE quality_factors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL,
    factor_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    INDEX idx_article_factor (article_id, factor_name)
);

-- Create a user for the application

CREATE USER IF NOT EXISTS 'article_user'@'localhost' IDENTIFIED BY 'article_password_123';
GRANT ALL PRIVILEGES ON article_summary_db.* TO 'article_user'@'localhost';
FLUSH PRIVILEGES;

-- Verify
SHOW TABLES;
DESCRIBE articles;
DESCRIBE quality_factors;
