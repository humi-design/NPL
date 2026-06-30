"""
MySQL Database Module for Job Card Management System
Handles all database operations including CRUD for job cards, items, materials, and GRN.
"""

import os
import mysql.connector
from mysql.connector import Error, pooling
from datetime import datetime
from typing import List, Dict, Optional, Any
import json


# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'job_card_db')
}


class DatabaseManager:
    """Manages MySQL database connections and operations."""
    
    _connection_pool = None
    
    @classmethod
    def get_connection_pool(cls):
        """Get or create the database connection pool."""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pooling.MySQLConnectionPool(
                    pool_name="job_card_pool",
                    pool_size=5,
                    pool_reset_session=True,
                    **DB_CONFIG
                )
            except Error as e:
                print(f"Error creating connection pool: {e}")
                return None
        return cls._connection_pool
    
    @classmethod
    def get_connection(cls):
        """Get a connection from the pool."""
        pool = cls.get_connection_pool()
        if pool:
            try:
                return pool.get_connection()
            except Error as e:
                print(f"Error getting connection: {e}")
                return None
        return None
    
    @classmethod
    def execute_query(cls, query: str, params: tuple = None, fetch: bool = True):
        """Execute a query and optionally return results."""
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return cursor.lastrowid
        except Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    
    @classmethod
    def execute_many(cls, query: str, data: List[tuple]):
        """Execute multiple queries at once."""
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            if conn and conn.is_connected():
                cursor = conn.cursor()
                cursor.executemany(query, data)
                conn.commit()
                return True
        except Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()


class JobCardDatabase:
    """Handles all job card related database operations."""
    
    @staticmethod
    def init_database():
        """Initialize the database and create all tables."""
        # First create database if it doesn't exist
        conn = None
        cursor = None
        try:
            config = DB_CONFIG.copy()
            db_name = config.pop('database')
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            conn.commit()
        except Error as e:
            print(f"Error creating database: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
        
        # Now create tables
        JobCardDatabase.create_tables()
        return True
    
    @staticmethod
    def create_tables():
        """Create all necessary tables."""
        queries = [
            # Job Cards Table
            """
            CREATE TABLE IF NOT EXISTS job_cards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_no VARCHAR(50) UNIQUE NOT NULL,
                job_date DATE NOT NULL,
                company_name VARCHAR(255),
                company_address TEXT,
                logo_data LONGTEXT,
                vendor_id VARCHAR(50),
                vendor_company VARCHAR(255),
                vendor_person VARCHAR(255),
                vendor_mobile VARCHAR(20),
                vendor_gst VARCHAR(50),
                vendor_address TEXT,
                dispatch_location VARCHAR(255),
                qr_code_data TEXT,
                expected_delivery_date DATE,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_job_card_no (job_card_no),
                INDEX idx_vendor_id (vendor_id),
                INDEX idx_status (status)
            )
            """,
            
            # Items Table
            """
            CREATE TABLE IF NOT EXISTS job_card_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                description VARCHAR(500),
                drawing_no VARCHAR(100),
                drawing_link VARCHAR(500),
                grade VARCHAR(100),
                quantity INT,
                uom VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # Materials Table
            """
            CREATE TABLE IF NOT EXISTS job_card_materials (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                raw_material VARCHAR(255),
                heat_no VARCHAR(100),
                dia_size VARCHAR(100),
                weight DECIMAL(10, 3),
                quantity INT,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # Operations Table
            """
            CREATE TABLE IF NOT EXISTS job_card_operations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                operation_name VARCHAR(100),
                is_selected BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # Machine Details Table
            """
            CREATE TABLE IF NOT EXISTS job_card_machine_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                machine_type VARCHAR(50),
                cycle_time VARCHAR(50),
                rpm VARCHAR(50),
                feed_rate VARCHAR(50),
                gear_setup VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # Quality Instructions Table
            """
            CREATE TABLE IF NOT EXISTS job_card_quality (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                tolerance VARCHAR(100),
                surface_finish VARCHAR(100),
                hardness VARCHAR(100),
                thread_check BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # GRN Table
            """
            CREATE TABLE IF NOT EXISTS job_card_grn (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                grn_date DATE,
                qty_received INT,
                ok_qty INT,
                rejected_qty INT,
                remarks TEXT,
                qc_approved_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """,
            
            # Signature Table
            """
            CREATE TABLE IF NOT EXISTS job_card_signatures (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_card_id INT NOT NULL,
                prepared_by VARCHAR(255),
                prepared_date DATE,
                qc_approved_by VARCHAR(255),
                qc_approved_date DATE,
                vendor_signed_by VARCHAR(255),
                vendor_signed_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_card_id) REFERENCES job_cards(id) ON DELETE CASCADE
            )
            """
        ]
        
        for query in queries:
            DatabaseManager.execute_query(query, fetch=False)
    
    @staticmethod
    def save_job_card(data: Dict[str, Any]) -> Optional[int]:
        """Save a complete job card with all related data."""
        try:
            # Insert main job card
            job_card_query = """
                INSERT INTO job_cards (
                    job_card_no, job_date, company_name, company_address, logo_data,
                    vendor_id, vendor_company, vendor_person, vendor_mobile, vendor_gst, vendor_address,
                    dispatch_location, qr_code_data, expected_delivery_date, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            job_card_id = DatabaseManager.execute_query(
                job_card_query,
                (
                    data.get('job_card_no'),
                    data.get('job_date'),
                    data.get('company_name'),
                    data.get('company_address'),
                    data.get('logo_data'),
                    data.get('vendor_id'),
                    data.get('vendor_company'),
                    data.get('vendor_person'),
                    data.get('vendor_mobile'),
                    data.get('vendor_gst'),
                    data.get('vendor_address'),
                    data.get('dispatch_location'),
                    data.get('qr_code_data'),
                    data.get('expected_delivery_date'),
                    data.get('status', 'Pending')
                ),
                fetch=False
            )
            
            if job_card_id:
                # Insert items
                for item in data.get('items', []):
                    JobCardDatabase.save_item(job_card_id, item)
                
                # Insert materials
                for material in data.get('materials', []):
                    JobCardDatabase.save_material(job_card_id, material)
                
                # Insert operations
                for operation in data.get('operations', []):
                    JobCardDatabase.save_operation(job_card_id, operation)
                
                # Insert machine details
                if data.get('machine_details'):
                    JobCardDatabase.save_machine_details(job_card_id, data.get('machine_details'))
                
                # Insert quality instructions
                if data.get('quality'):
                    JobCardDatabase.save_quality(job_card_id, data.get('quality'))
                
                # Insert GRN entries
                for grn in data.get('grn_entries', []):
                    JobCardDatabase.save_grn(job_card_id, grn)
                
                # Insert signatures
                if data.get('signatures'):
                    JobCardDatabase.save_signatures(job_card_id, data.get('signatures'))
            
            return job_card_id
        except Error as e:
            print(f"Error saving job card: {e}")
            return None
    
    @staticmethod
    def save_item(job_card_id: int, item: Dict[str, Any]):
        """Save an item for a job card."""
        query = """
            INSERT INTO job_card_items 
            (job_card_id, description, drawing_no, drawing_link, grade, quantity, uom)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, item.get('description'), item.get('drawing_no'),
             item.get('drawing_link'), item.get('grade'), item.get('quantity'), item.get('uom')),
            fetch=False
        )
    
    @staticmethod
    def save_material(job_card_id: int, material: Dict[str, Any]):
        """Save a material for a job card."""
        query = """
            INSERT INTO job_card_materials 
            (job_card_id, raw_material, heat_no, dia_size, weight, quantity, remark)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, material.get('raw_material'), material.get('heat_no'),
             material.get('dia_size'), material.get('weight'), material.get('quantity'),
             material.get('remark')),
            fetch=False
        )
    
    @staticmethod
    def save_operation(job_card_id: int, operation: Dict[str, str]):
        """Save an operation for a job card."""
        query = """
            INSERT INTO job_card_operations (job_card_id, operation_name, is_selected)
            VALUES (%s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, operation.get('name'), operation.get('selected', False)),
            fetch=False
        )
    
    @staticmethod
    def save_machine_details(job_card_id: int, details: Dict[str, Any]):
        """Save machine details for a job card."""
        query = """
            INSERT INTO job_card_machine_details 
            (job_card_id, machine_type, cycle_time, rpm, feed_rate, gear_setup)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, details.get('machine_type'), details.get('cycle_time'),
             details.get('rpm'), details.get('feed_rate'), details.get('gear_setup')),
            fetch=False
        )
    
    @staticmethod
    def save_quality(job_card_id: int, quality: Dict[str, Any]):
        """Save quality instructions for a job card."""
        query = """
            INSERT INTO job_card_quality 
            (job_card_id, tolerance, surface_finish, hardness, thread_check)
            VALUES (%s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, quality.get('tolerance'), quality.get('surface_finish'),
             quality.get('hardness'), quality.get('thread_check')),
            fetch=False
        )
    
    @staticmethod
    def save_grn(job_card_id: int, grn: Dict[str, Any]):
        """Save a GRN entry for a job card."""
        query = """
            INSERT INTO job_card_grn 
            (job_card_id, grn_date, qty_received, ok_qty, rejected_qty, remarks, qc_approved_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, grn.get('date'), grn.get('qty_received'), grn.get('ok_qty'),
             grn.get('rejected_qty'), grn.get('remarks'), grn.get('qc_approved_by')),
            fetch=False
        )
    
    @staticmethod
    def save_signatures(job_card_id: int, signatures: Dict[str, Any]):
        """Save signature information for a job card."""
        query = """
            INSERT INTO job_card_signatures 
            (job_card_id, prepared_by, prepared_date, qc_approved_by, qc_approved_date, 
             vendor_signed_by, vendor_signed_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        DatabaseManager.execute_query(
            query,
            (job_card_id, signatures.get('prepared_by'), signatures.get('prepared_date'),
             signatures.get('qc_approved_by'), signatures.get('qc_approved_date'),
             signatures.get('vendor_signed_by'), signatures.get('vendor_signed_date')),
            fetch=False
        )
    
    @staticmethod
    def get_job_card(job_card_no: str) -> Optional[Dict[str, Any]]:
        """Get a complete job card with all related data."""
        # Get main job card
        job_card_query = "SELECT * FROM job_cards WHERE job_card_no = %s"
        job_card = DatabaseManager.execute_query(job_card_query, (job_card_no,))
        
        if not job_card:
            return None
        
        job_card = job_card[0]
        job_card_id = job_card['id']
        
        # Get items
        items_query = "SELECT * FROM job_card_items WHERE job_card_id = %s"
        items = DatabaseManager.execute_query(items_query, (job_card_id,))
        
        # Get materials
        materials_query = "SELECT * FROM job_card_materials WHERE job_card_id = %s"
        materials = DatabaseManager.execute_query(materials_query, (job_card_id,))
        
        # Get operations
        operations_query = "SELECT * FROM job_card_operations WHERE job_card_id = %s"
        operations = DatabaseManager.execute_query(operations_query, (job_card_id,))
        
        # Get machine details
        machine_query = "SELECT * FROM job_card_machine_details WHERE job_card_id = %s"
        machine_details = DatabaseManager.execute_query(machine_query, (job_card_id,))
        
        # Get quality
        quality_query = "SELECT * FROM job_card_quality WHERE job_card_id = %s"
        quality = DatabaseManager.execute_query(quality_query, (job_card_id,))
        
        # Get GRN entries
        grn_query = "SELECT * FROM job_card_grn WHERE job_card_id = %s"
        grn_entries = DatabaseManager.execute_query(grn_query, (job_card_id,))
        
        # Get signatures
        signatures_query = "SELECT * FROM job_card_signatures WHERE job_card_id = %s"
        signatures = DatabaseManager.execute_query(signatures_query, (job_card_id,))
        
        return {
            'job_card': job_card,
            'items': items,
            'materials': materials,
            'operations': operations,
            'machine_details': machine_details[0] if machine_details else None,
            'quality': quality[0] if quality else None,
            'grn_entries': grn_entries,
            'signatures': signatures[0] if signatures else None
        }
    
    @staticmethod
    def get_all_job_cards(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all job cards with optional status filter."""
        if status:
            query = "SELECT * FROM job_cards WHERE status = %s ORDER BY created_at DESC"
            return DatabaseManager.execute_query(query, (status,)) or []
        else:
            query = "SELECT * FROM job_cards ORDER BY created_at DESC"
            return DatabaseManager.execute_query(query) or []
    
    @staticmethod
    def update_job_card_status(job_card_no: str, status: str) -> bool:
        """Update the status of a job card."""
        query = "UPDATE job_cards SET status = %s WHERE job_card_no = %s"
        result = DatabaseManager.execute_query(query, (status, job_card_no), fetch=False)
        return result is not None
    
    @staticmethod
    def delete_job_card(job_card_no: str) -> bool:
        """Delete a job card and all related data (CASCADE)."""
        query = "DELETE FROM job_cards WHERE job_card_no = %s"
        result = DatabaseManager.execute_query(query, (job_card_no,), fetch=False)
        return result is not None
    
    @staticmethod
    def search_job_cards(search_term: str) -> List[Dict[str, Any]]:
        """Search job cards by various fields."""
        query = """
            SELECT * FROM job_cards 
            WHERE job_card_no LIKE %s 
            OR vendor_company LIKE %s 
            OR vendor_id LIKE %s
            ORDER BY created_at DESC
        """
        search = f"%{search_term}%"
        return DatabaseManager.execute_query(query, (search, search, search)) or []
    
    @staticmethod
    def get_job_cards_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get job cards within a date range."""
        query = """
            SELECT * FROM job_cards 
            WHERE job_date BETWEEN %s AND %s 
            ORDER BY job_date DESC
        """
        return DatabaseManager.execute_query(query, (start_date, end_date)) or []
    
    @staticmethod
    def get_job_card_statistics() -> Dict[str, Any]:
        """Get statistics about job cards."""
        stats = {}
        
        # Total job cards
        total = DatabaseManager.execute_query("SELECT COUNT(*) as count FROM job_cards")
        stats['total'] = total[0]['count'] if total else 0
        
        # By status
        by_status = DatabaseManager.execute_query(
            "SELECT status, COUNT(*) as count FROM job_cards GROUP BY status"
        ) or []
        stats['by_status'] = {row['status']: row['count'] for row in by_status}
        
        # This month
        this_month = DatabaseManager.execute_query(
            "SELECT COUNT(*) as count FROM job_cards WHERE MONTH(job_date) = MONTH(CURRENT_DATE())"
        )
        stats['this_month'] = this_month[0]['count'] if this_month else 0
        
        return stats


def init_database():
    """Initialize the database - wrapper function."""
    return JobCardDatabase.init_database()


def save_job_card(data: Dict[str, Any]) -> Optional[int]:
    """Save job card - wrapper function."""
    return JobCardDatabase.save_job_card(data)


def get_job_card(job_card_no: str) -> Optional[Dict[str, Any]]:
    """Get job card - wrapper function."""
    return JobCardDatabase.get_job_card(job_card_no)


def get_all_job_cards(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all job cards - wrapper function."""
    return JobCardDatabase.get_all_job_cards(status)


def update_job_card_status(job_card_no: str, status: str) -> bool:
    """Update job card status - wrapper function."""
    return JobCardDatabase.update_job_card_status(job_card_no, status)


def delete_job_card(job_card_no: str) -> bool:
    """Delete job card - wrapper function."""
    return JobCardDatabase.delete_job_card(job_card_no)


def search_job_cards(search_term: str) -> List[Dict[str, Any]]:
    """Search job cards - wrapper function."""
    return JobCardDatabase.search_job_cards(search_term)


def get_job_card_statistics() -> Dict[str, Any]:
    """Get job card statistics - wrapper function."""
    return JobCardDatabase.get_job_card_statistics()
