"""
خدمة البريد الإلكتروني - JobSpy
Email service for JobSpy
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

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
            subject = f"🔔 تنبيه وظائف جديدة - {alert_query}"
            
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
            subject = "مرحباً بك في JobSpy"
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
            subject = "إعادة تعيين كلمة المرور - JobSpy"
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
            subject = "تأكيد بريدك الإلكتروني - JobSpy"
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
                    <strong>الشركة:</strong> {job.get('company', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>الموقع:</strong> {job.get('location', 'N/A')}
                </p>
                <p style="margin: 5px 0; color: #666;">
                    <strong>نوع الوظيفة:</strong> {job.get('job_type', 'N/A')}
                </p>
                {f'<p style="margin: 5px 0; color: #666;"><strong>الراتب:</strong> {job.get("salary_min", "N/A")} - {job.get("salary_max", "N/A")} {job.get("salary_currency", "USD")}</p>' if job.get('salary_min') or job.get('salary_max') else ''}
            </div>
            """
        
        return f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 تنبيه وظائف جديدة</h1>
                </div>
                <div class="content">
                    <p>مرحباً،</p>
                    <p>وجدنا <strong>{len(new_jobs)}</strong> وظائف جديدة تطابق معايير البحث الخاصة بك:</p>
                    <p><strong>البحث:</strong> {alert_query}</p>
                    <p><strong>التكرار:</strong> {alert_frequency}</p>
                    <hr>
                    {jobs_html}
                    <hr>
                    <p>
                        <a href="{settings.FRONTEND_URL}/jobs" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            عرض جميع الوظائف
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 JobSpy. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_welcome_email_body(user_name: str) -> str:
        """Build welcome email HTML body."""
        return f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>مرحباً بك في JobSpy</h1>
                </div>
                <div class="content">
                    <p>مرحباً {user_name}،</p>
                    <p>شكراً لتسجيلك في JobSpy! نحن سعداء بانضمامك إلينا.</p>
                    <p>يمكنك الآن:</p>
                    <ul>
                        <li>البحث عن الوظائف المناسبة لك</li>
                        <li>حفظ الوظائف المفضلة</li>
                        <li>إنشاء تنبيهات للوظائف الجديدة</li>
                        <li>إدارة ملفك الشخصي</li>
                    </ul>
                    <p>
                        <a href="{settings.FRONTEND_URL}/jobs" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            ابدأ البحث الآن
                        </a>
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 JobSpy. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_password_reset_email_body(reset_url: str) -> str:
        """Build password reset email HTML body."""
        return f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>إعادة تعيين كلمة المرور</h1>
                </div>
                <div class="content">
                    <p>مرحباً،</p>
                    <p>لقد طلبت إعادة تعيين كلمة المرور الخاصة بك. انقر على الزر أدناه لإعادة تعيين كلمة المرور:</p>
                    <p>
                        <a href="{reset_url}" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            إعادة تعيين كلمة المرور
                        </a>
                    </p>
                    <p>إذا لم تطلب هذا، يرجى تجاهل هذا البريد الإلكتروني.</p>
                    <p>ملاحظة: هذا الرابط صالح لمدة 24 ساعة فقط.</p>
                </div>
                <div class="footer">
                    <p>© 2024 JobSpy. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _build_verification_email_body(verification_url: str) -> str:
        """Build email verification HTML body."""
        return f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0066cc; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>تأكيد بريدك الإلكتروني</h1>
                </div>
                <div class="content">
                    <p>مرحباً،</p>
                    <p>شكراً لتسجيلك في JobSpy! يرجى تأكيد بريدك الإلكتروني بالنقر على الزر أدناه:</p>
                    <p>
                        <a href="{verification_url}" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            تأكيد البريد الإلكتروني
                        </a>
                    </p>
                    <p>إذا لم تقم بالتسجيل، يرجى تجاهل هذا البريد الإلكتروني.</p>
                </div>
                <div class="footer">
                    <p>© 2024 JobSpy. جميع الحقوق محفوظة.</p>
                </div>
            </div>
        </body>
        </html>
        """
