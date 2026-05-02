"""
Email Service - JobSpy
Email service for JobSpy
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for handling email operations."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD
    
    async def send_alert_email(
        self,
        recipient_email: str,
        alert_query: str,
        new_jobs: List[Dict[str, Any]],
        alert_frequency: str,
    ) -> bool:
        """
        Send alert email with new jobs.
        
        Args:
            recipient_email: Recipient email address
            alert_query: Alert search query
            new_jobs: List of new jobs found
            alert_frequency: Alert frequency
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = f"ðŸ”” New Job Alert - {alert_query}"
            
            # Build email body
            body = self._build_alert_email_body(alert_query, new_jobs, alert_frequency)
            
            # Send email
            await self._send_email(recipient_email, subject, body)
            
            logger.info(f"Alert email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending alert email: {str(e)}")
            return False
    
    async def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """
        Send welcome email to new user.
        
        Args:
            recipient_email: Recipient email address
            user_name: User name
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = "Welcome to JobSpy"
            body = self._build_welcome_email_body(user_name)
            
            await self._send_email(recipient_email, subject, body)
            
            logger.info(f"Welcome email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    async def send_password_reset_email(
        self,
        recipient_email: str,
        reset_token: str,
        reset_url: str,
    ) -> bool:
        """
        Send password reset email.
        
        Args:
            recipient_email: Recipient email address
            reset_token: Password reset token
            reset_url: Password reset URL
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = "Reset Password - JobSpy"
            body = self._build_password_reset_email_body(reset_url)
            
            await self._send_email(recipient_email, subject, body)
            
            logger.info(f"Password reset email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    async def send_verification_email(
        self,
        recipient_email: str,
        verification_token: str,
        verification_url: str,
    ) -> bool:
        """
        Send email verification email.
        
        Args:
            recipient_email: Recipient email address
            verification_token: Email verification token
            verification_url: Email verification URL
        
        Returns:
            True if email sent successfully
        """
        try:
            subject = "Confirm your email - JobSpy"
            body = self._build_verification_email_body(verification_url)
            
            await self._send_email(recipient_email, subject, body)
            
            logger.info(f"Verification email sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False
    
    async def _send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        Send email using SMTP.
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body (HTML)
        
        Returns:
            True if email sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Attach HTML body
            html_part = MIMEText(body, "html", "utf-8")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {str(e)}")
            return False
    
    @staticmethod
    def _build_alert_email_body(
        alert_query: str,
        new_jobs: List[Dict[str, Any]],
        alert_frequency: str,
    ) -> str:
        """Build alert email HTML body."""
        jobs_html = ""
        for job in new_jobs[:10]:  # Limit to 10 jobs per email
            jobs_html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    <a href="{job.get('source_url', '#')}" style="color: #0066cc; text-decoration: none;">
                        {job.get('title', 'N/A')}
                    </a>
                </h3>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Company:</strong> {job.get('company', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Location:</strong> {job.get('location', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>Job Type:</strong> {job.get('job_type', 'N/A')}
                </p>
                {f'<p style="margin: 5px 0; color: #666;"><strong>Salary:</strong> {job.get("salary_min", "N/A")} - {job.get("salary_max", "N/A")} {job.get("salary_currency", "USD")}</p>' if job.get('salary_min') or job.get('salary_max') else ''}
            </div>
            """
        
        return f"""
        <html dir="ltr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: ltr; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>ðŸ”” New Job Alert</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>We found <strong>{len(new_jobs)}</strong> new jobs matching your search criteria:</p>
                    <p><strong>Search:</strong> {alert_query}</p>
                    <p><strong>Frequency:</strong> {alert_frequency}</p>
                    <hr>
                    {jobs_html}
                    <hr>
                    <p>
                        <a href="{settings.FRONTEND_URL}/jobs" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View all jobs
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>Â© 2024 JobSpy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_welcome_email_body(user_name: str) -> str:
        """Build welcome email HTML body."""
        return f"""
        <html dir="ltr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: ltr; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to JobSpy</h1>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>Thank you for registering at JobSpy! We're glad to have you.</p>
                    <p>You can now:</p>
                    <ul>
                        <li>Search for suitable jobs</li>
                        <li>Save favorite jobs</li>
                        <li>Create alerts for new jobs</li>
                        <li>Manage your profile</li>
                    </ul>
                    <p>
                        <a href="{settings.FRONTEND_URL}/jobs" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Start searching now
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>Â© 2024 JobSpy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_password_reset_email_body(reset_url: str) -> str:
        """Build password reset email HTML body."""
        return f"""
        <html dir="ltr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: ltr; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reset Password</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>You have requested to reset your password. Click the button below to reset it:</p>
                    <p>
                        <a href="{reset_url}" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Reset Password
                        </a>
                    </p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <p>Note: This link is valid for 24 hours only.</p>
                </div>
                <div class="footer">
                    <p>Â© 2024 JobSpy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_verification_email_body(verification_url: str) -> str:
        """Build email verification HTML body."""
        return f"""
        <html dir="ltr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: ltr; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirm your email</h1>
                </div>
                <div class="content">
                    <p>Hello,</p>
                    <p>Thank you for registering at JobSpy! Please confirm your email by clicking the button below:</p>
                    <p>
                        <a href="{verification_url}" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Confirm Email
                        </a>
                    </p>
                    <p>If you didn't register, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Â© 2024 JobSpy. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
