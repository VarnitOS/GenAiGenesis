#!/usr/bin/env python3
"""
API routes for vector database cleanup operations.

This module exposes endpoints for cleaning up vector database and S3 storage.
"""

import os
import sys
import json
import logging
from flask import Blueprint, request, jsonify

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import cleanup module
from data_pipeline.cleanup import VectorDBCleanup

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
cleanup_routes = Blueprint('cleanup', __name__)

# Initialize cleanup manager
cleanup_manager = VectorDBCleanup()

@cleanup_routes.route('/cleanup/vector-db', methods=['POST'])
def cleanup_vector_db():
    """
    API endpoint to clean up vector database and S3 storage
    
    Requires admin access token in Authorization header.
    
    Returns:
        JSON response with cleanup results
    """
    # Get authorization header
    auth_header = request.headers.get('Authorization')
    
    # Check admin access
    if not _is_admin_access(auth_header):
        logger.warning(f"Unauthorized cleanup attempt from {request.remote_addr}")
        return jsonify({
            'error': 'Unauthorized. Admin access required for database cleanup operations.'
        }), 401
    
    # Get confirmation from request body
    data = request.get_json() or {}
    confirmed = data.get('confirm', False)
    
    if not confirmed:
        return jsonify({
            'error': 'Unconfirmed operation. Set "confirm: true" in request body to proceed.'
        }), 400
    
    # Log cleanup request
    logger.info(f"Vector database cleanup requested by admin from {request.remote_addr}")
    
    try:
        # Perform cleanup
        result = cleanup_manager.cleanup_all()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Vector database cleanup completed successfully',
            'result': result
        })
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def _is_admin_access(auth_header: str) -> bool:
    """
    Check if the request has admin access
    
    Args:
        auth_header: Authorization header from request
        
    Returns:
        True if admin access is valid, False otherwise
    """
    # Get admin token from environment
    admin_token = os.environ.get('ADMIN_API_TOKEN')
    
    # If no admin token is set, reject all requests
    if not admin_token:
        logger.error("ADMIN_API_TOKEN not set in environment")
        return False
    
    # Parse auth header
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    # Extract token
    token = auth_header.split('Bearer ')[1].strip()
    
    # Compare with admin token (use constant time comparison for security)
    import hmac
    return hmac.compare_digest(token, admin_token) 