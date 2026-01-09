/**
 * Supabase Storage Service
 * Helper functions for file uploads using Supabase Storage
 */

import { supabase } from './supabase';
import * as ImagePicker from 'expo-image-picker';
import * as DocumentPicker from 'expo-document-picker';

/**
 * Upload file to Supabase Storage
 * @param {string} bucket - Bucket name (e.g., 'avatars', 'kyc-documents', 'vehicle-images')
 * @param {string} filePath - Path within bucket (e.g., 'user_123/avatar.jpg')
 * @param {File|Blob|ArrayBuffer} file - File to upload
 * @param {string} contentType - MIME type (e.g., 'image/jpeg')
 * @returns {Promise<{publicUrl: string, path: string}>}
 */
export const uploadFile = async (bucket, filePath, file, contentType = 'image/jpeg') => {
  try {
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(filePath, file, {
        contentType,
        upsert: false, // Don't overwrite existing files
      });

    if (error) throw error;

    // Get public URL
    const { data: { publicUrl } } = supabase.storage
      .from(bucket)
      .getPublicUrl(filePath);

    return {
      publicUrl,
      path: data.path,
    };
  } catch (error) {
    console.error('Upload error:', error);
    throw new Error(error.message || 'Failed to upload file');
  }
};

/**
 * Upload image from camera or gallery
 * @param {string} bucket - Bucket name
 * @param {string} folder - Folder within bucket
 * @param {Object} imagePickerResult - Result from ImagePicker
 * @returns {Promise<string>} Public URL of uploaded image
 */
export const uploadImage = async (bucket, folder, imagePickerResult) => {
  try {
    if (!imagePickerResult || imagePickerResult.canceled) {
      throw new Error('No image selected');
    }

    const asset = imagePickerResult.assets[0];
    const uri = asset.uri;

    // Create unique filename
    const fileName = `${Date.now()}_${Math.random().toString(36).substring(7)}.jpg`;
    const filePath = folder ? `${folder}/${fileName}` : fileName;

    // Fetch the image as blob
    const response = await fetch(uri);
    const blob = await response.blob();

    // Upload to Supabase
    const { publicUrl } = await uploadFile(bucket, filePath, blob, 'image/jpeg');

    return publicUrl;
  } catch (error) {
    console.error('Image upload error:', error);
    throw error;
  }
};

/**
 * Upload document (PDF, images, etc.)
 * @param {string} bucket - Bucket name
 * @param {string} folder - Folder within bucket
 * @param {Object} documentPickerResult - Result from DocumentPicker
 * @returns {Promise<string>} Public URL of uploaded document
 */
export const uploadDocument = async (bucket, folder, documentPickerResult) => {
  try {
    if (!documentPickerResult || documentPickerResult.type === 'cancel') {
      throw new Error('No document selected');
    }

    const asset = documentPickerResult.assets?.[0] || documentPickerResult;
    const uri = asset.uri;
    const mimeType = asset.mimeType || 'application/octet-stream';
    const name = asset.name || `document_${Date.now()}`;

    // Create file path
    const filePath = folder ? `${folder}/${name}` : name;

    // Fetch the document as blob
    const response = await fetch(uri);
    const blob = await response.blob();

    // Upload to Supabase
    const { publicUrl } = await uploadFile(bucket, filePath, blob, mimeType);

    return publicUrl;
  } catch (error) {
    console.error('Document upload error:', error);
    throw error;
  }
};

/**
 * Upload user avatar/profile picture
 * @param {string} userId - User ID
 * @param {Object} imagePickerResult - Result from ImagePicker
 * @returns {Promise<string>} Public URL of avatar
 */
export const uploadAvatar = async (userId, imagePickerResult) => {
  return uploadImage('avatars', userId, imagePickerResult);
};

/**
 * Upload KYC document
 * @param {string} userId - User ID
 * @param {string} documentType - Type of document (e.g., 'emirates_id', 'passport', 'driving_license')
 * @param {string} side - Document side ('front', 'back', or 'visa')
 * @param {Object} imagePickerResult - Result from ImagePicker
 * @returns {Promise<string>} Public URL of document
 */
export const uploadKYCDocument = async (userId, documentType, side, imagePickerResult) => {
  const folder = `${userId}/${documentType}`;
  return uploadImage('kyc-documents', folder, imagePickerResult);
};

/**
 * Upload vehicle image
 * @param {string} vehicleId - Vehicle ID
 * @param {Object} imagePickerResult - Result from ImagePicker
 * @returns {Promise<string>} Public URL of vehicle image
 */
export const uploadVehicleImage = async (vehicleId, imagePickerResult) => {
  return uploadImage('vehicle-images', vehicleId, imagePickerResult);
};

/**
 * Delete file from Supabase Storage
 * @param {string} bucket - Bucket name
 * @param {string} filePath - Path to file in bucket
 * @returns {Promise<boolean>}
 */
export const deleteFile = async (bucket, filePath) => {
  try {
    const { error } = await supabase.storage
      .from(bucket)
      .remove([filePath]);

    if (error) throw error;

    return true;
  } catch (error) {
    console.error('Delete error:', error);
    throw error;
  }
};

/**
 * Get public URL for a file
 * @param {string} bucket - Bucket name
 * @param {string} filePath - Path to file in bucket
 * @returns {string} Public URL
 */
export const getPublicUrl = (bucket, filePath) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(filePath);

  return data.publicUrl;
};

/**
 * List files in a bucket folder
 * @param {string} bucket - Bucket name
 * @param {string} folder - Folder path (optional)
 * @returns {Promise<Array>} List of files
 */
export const listFiles = async (bucket, folder = '') => {
  try {
    const { data, error } = await supabase.storage
      .from(bucket)
      .list(folder);

    if (error) throw error;

    return data;
  } catch (error) {
    console.error('List files error:', error);
    throw error;
  }
};

/**
 * Request camera permissions
 * @returns {Promise<boolean>}
 */
export const requestCameraPermission = async () => {
  try {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    return status === 'granted';
  } catch (error) {
    console.error('Camera permission error:', error);
    return false;
  }
};

/**
 * Request media library permissions
 * @returns {Promise<boolean>}
 */
export const requestMediaLibraryPermission = async () => {
  try {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    return status === 'granted';
  } catch (error) {
    console.error('Media library permission error:', error);
    return false;
  }
};

/**
 * Pick image from camera
 * @param {Object} options - ImagePicker options
 * @returns {Promise<Object>} ImagePicker result
 */
export const pickImageFromCamera = async (options = {}) => {
  try {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) {
      throw new Error('Camera permission denied');
    }

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
      ...options,
    });

    return result;
  } catch (error) {
    console.error('Pick from camera error:', error);
    throw error;
  }
};

/**
 * Pick image from gallery
 * @param {Object} options - ImagePicker options
 * @returns {Promise<Object>} ImagePicker result
 */
export const pickImageFromGallery = async (options = {}) => {
  try {
    const hasPermission = await requestMediaLibraryPermission();
    if (!hasPermission) {
      throw new Error('Media library permission denied');
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
      ...options,
    });

    return result;
  } catch (error) {
    console.error('Pick from gallery error:', error);
    throw error;
  }
};

/**
 * Pick document
 * @param {Object} options - DocumentPicker options
 * @returns {Promise<Object>} DocumentPicker result
 */
export const pickDocument = async (options = {}) => {
  try {
    const result = await DocumentPicker.getDocumentAsync({
      type: '*/*',
      copyToCacheDirectory: true,
      ...options,
    });

    return result;
  } catch (error) {
    console.error('Pick document error:', error);
    throw error;
  }
};

export default {
  uploadFile,
  uploadImage,
  uploadDocument,
  uploadAvatar,
  uploadKYCDocument,
  uploadVehicleImage,
  deleteFile,
  getPublicUrl,
  listFiles,
  requestCameraPermission,
  requestMediaLibraryPermission,
  pickImageFromCamera,
  pickImageFromGallery,
  pickDocument,
};

