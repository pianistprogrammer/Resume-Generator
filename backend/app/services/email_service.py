"""Email service for sending notifications via SMTP."""

import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
from functools import partial

from app.config import settings


class EmailService:
    """Service for sending emails via SMTP."""

    @staticmethod
    def _send_email_sync(
        to_email: str | List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP (synchronous).

        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content (fallback)

        Returns:
            bool: True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.email_from_name} <{settings.email_user}>"

            # Handle multiple recipients
            if isinstance(to_email, list):
                msg['To'] = ", ".join(to_email)
                recipients = to_email
            else:
                msg['To'] = to_email
                recipients = [to_email]

            # Add plain text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Connect to SMTP server with timeout
            if settings.email_use_ssl:
                # Use SMTP_SSL for port 465
                server = smtplib.SMTP_SSL(settings.email_host, settings.email_port, timeout=10)
            else:
                server = smtplib.SMTP(settings.email_host, settings.email_port, timeout=10)
                if settings.email_use_tls:
                    server.starttls()

            # Login and send
            server.login(settings.email_user, settings.email_pass)
            server.sendmail(settings.email_user, recipients, msg.as_string())
            server.quit()

            print(f"✓ Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            print(f"✗ Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    async def send_email(
        to_email: str | List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP (async wrapper).

        Runs the synchronous email sending in a thread pool to avoid blocking.
        """
        loop = asyncio.get_event_loop()
        func = partial(
            EmailService._send_email_sync,
            to_email,
            subject,
            html_content,
            text_content
        )
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, func),
                timeout=15.0  # 15 second timeout
            )
        except asyncio.TimeoutError:
            print(f"✗ Email sending timed out for {to_email}")
            return False
        except Exception as e:
            print(f"✗ Email sending failed: {e}")
            return False

    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str) -> bool:
        """Send welcome email to new user."""
        subject = f"Welcome to {settings.app_name}! 🎉"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #059669; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .feature {{ margin: 15px 0; padding: 15px; background: white; border-radius: 8px; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{settings.app_name}</h1>
                    <p>Your AI-powered job hunting assistant</p>
                </div>
                <div class="content">
                    <h2>Welcome, {user_name}! 👋</h2>
                    <p>We're excited to help you find your perfect job match. Here's what you can do:</p>

                    <div class="feature">
                        <strong>🎯 Smart Matching</strong><br>
                        AI scores every job against your profile to find the best matches.
                    </div>

                    <div class="feature">
                        <strong>✨ AI-Tailored Resumes</strong><br>
                        Generate ATS-optimized resumes in seconds with Claude AI.
                    </div>

                    <div class="feature">
                        <strong>📧 Daily Digests</strong><br>
                        Get your top job matches delivered every evening at 6 PM.
                    </div>

                    <p>You have <strong>{settings.free_credits} free resume credits</strong> to get started!</p>

                    <p style="text-align: center;">
                        <a href="{settings.cors_origins[0]}/onboarding" class="button">Complete Your Profile</a>
                    </p>

                    <p>Questions? Just reply to this email – we're here to help!</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} {settings.app_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to {settings.app_name}, {user_name}!

        We're excited to help you find your perfect job match.

        What you can do:
        - Smart Matching: AI scores jobs against your profile
        - AI-Tailored Resumes: Generate ATS-optimized resumes in seconds
        - Daily Digests: Get top matches delivered every evening

        You have {settings.free_credits} free resume credits to get started!

        Complete your profile: {settings.cors_origins[0]}/onboarding

        Questions? Just reply to this email.
        """

        return await EmailService.send_email(user_email, subject, html_content, text_content)

    @staticmethod
    async def send_password_reset_email(user_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.cors_origins[0]}/reset-password?token={reset_token}"
        subject = "Reset Your Password"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 10px; }}
                .button {{ display: inline-block; background: #059669; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password for your {settings.app_name} account.</p>

                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>

                    <div class="warning">
                        <strong>⚠️ Security Notice</strong><br>
                        This link will expire in 1 hour. If you didn't request this, please ignore this email.
                    </div>

                    <p>Or copy and paste this URL into your browser:<br>
                    <code>{reset_url}</code></p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        We received a request to reset your password for your {settings.app_name} account.

        Reset your password: {reset_url}

        This link will expire in 1 hour. If you didn't request this, please ignore this email.
        """

        return await EmailService.send_email(user_email, subject, html_content, text_content)

    @staticmethod
    async def send_resume_ready_notification(user_email: str, user_name: str, job_title: str, company: str, resume_id: str) -> bool:
        """Send notification when resume is ready."""
        resume_url = f"{settings.cors_origins[0]}/resumes/{resume_id}"
        subject = f"✨ Your Resume is Ready for {job_title} at {company}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 10px; }}
                .button {{ display: inline-block; background: #059669; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; }}
                .job-card {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h2>Your Resume is Ready! ✨</h2>
                    <p>Hi {user_name},</p>

                    <p>Great news! Your AI-tailored resume is ready for:</p>

                    <div class="job-card">
                        <h3 style="margin: 0 0 10px 0;">{job_title}</h3>
                        <p style="color: #059669; margin: 0;"><strong>{company}</strong></p>
                    </div>

                    <p>Your resume has been optimized for ATS systems and tailored to match the job requirements.</p>

                    <p style="text-align: center;">
                        <a href="{resume_url}" class="button">View & Download Resume</a>
                    </p>

                    <p>Good luck with your application! 🚀</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Your Resume is Ready!

        Hi {user_name},

        Great news! Your AI-tailored resume is ready for:
        {job_title} at {company}

        View and download: {resume_url}

        Good luck with your application!
        """

        return await EmailService.send_email(user_email, subject, html_content, text_content)

    @staticmethod
    async def send_daily_digest(user_email: str, user_name: str, matches: list) -> bool:
        """Send daily job matches digest."""
        subject = f"📬 Your Daily Job Matches - {datetime.now().strftime('%B %d, %Y')}"

        # Build matches HTML
        matches_html = ""
        for match in matches[:5]:  # Top 5 matches
            matches_html += f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0 0 5px 0;">{match.get('title', 'Job Title')}</h3>
                        <p style="color: #059669; margin: 0 0 10px 0;"><strong>{match.get('company', 'Company')}</strong></p>
                        <p style="color: #6b7280; margin: 0;">{match.get('location', 'Location')}</p>
                    </div>
                    <div style="text-align: center;">
                        <div style="background: #dcfce7; color: #059669; font-weight: bold; padding: 8px 16px; border-radius: 8px;">
                            {match.get('score', 0)}%
                        </div>
                        <p style="font-size: 12px; color: #6b7280; margin: 5px 0 0 0;">Match</p>
                    </div>
                </div>
                <p style="text-align: center; margin: 15px 0 0 0;">
                    <a href="{settings.cors_origins[0]}/jobs/{match.get('id')}" class="button-small">View Details</a>
                </p>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .job-card {{ background: white; padding: 20px; border-radius: 8px; margin: 15px 0; border: 1px solid #e5e7eb; }}
                .button-small {{ display: inline-block; background: #059669; color: white; padding: 8px 20px; text-decoration: none; border-radius: 6px; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Daily Job Matches</h1>
                    <p>{datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>We found <strong>{len(matches)} new job matches</strong> for you today! Here are your top picks:</p>

                    {matches_html}

                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{settings.cors_origins[0]}/matches" class="button-small">View All Matches →</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Build text version
        matches_text = "\n".join([
            f"- {m.get('title', 'Job')} at {m.get('company', 'Company')} ({m.get('score', 0)}% match)"
            for m in matches[:5]
        ])

        text_content = f"""
        Your Daily Job Matches - {datetime.now().strftime('%B %d, %Y')}

        Hi {user_name},

        We found {len(matches)} new job matches for you today!

        Top Matches:
        {matches_text}

        View all matches: {settings.cors_origins[0]}/matches
        """

        return await EmailService.send_email(user_email, subject, html_content, text_content)
