/**
 * RubricManager.gs
 * Handles rubric storage, retrieval, and management
 */

/**
 * Save a rubric to user properties
 */
function saveRubric(rubric) {
  try {
    var userProps = PropertiesService.getUserProperties();
    var rubrics = getAllRubrics();

    // Generate ID if new rubric
    if (!rubric.id) {
      rubric.id = Utilities.getUuid();
      rubric.createdAt = new Date().toISOString();
    }
    rubric.updatedAt = new Date().toISOString();

    // Add or update rubric
    rubrics[rubric.id] = rubric;

    // Save back to properties (with size limit handling)
    var rubricsJson = JSON.stringify(rubrics);
    if (rubricsJson.length > 9000) {
      // Properties have a 9KB limit, so we might need to split
      Logger.log('Warning: Rubrics approaching storage limit');
    }
    userProps.setProperty('rubrics', rubricsJson);

    return { success: true, id: rubric.id };
  } catch (error) {
    Logger.log('Error saving rubric: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Get all saved rubrics
 */
function getAllRubrics() {
  try {
    var userProps = PropertiesService.getUserProperties();
    var rubricsJson = userProps.getProperty('rubrics');

    if (!rubricsJson) {
      return {};
    }

    return JSON.parse(rubricsJson);
  } catch (error) {
    Logger.log('Error getting rubrics: ' + error.toString());
    return {};
  }
}

/**
 * Get a specific rubric by ID
 */
function getRubric(rubricId) {
  var rubrics = getAllRubrics();
  return rubrics[rubricId] || null;
}

/**
 * Delete a rubric
 */
function deleteRubric(rubricId) {
  try {
    var userProps = PropertiesService.getUserProperties();
    var rubrics = getAllRubrics();

    delete rubrics[rubricId];

    userProps.setProperty('rubrics', JSON.stringify(rubrics));
    return { success: true };
  } catch (error) {
    Logger.log('Error deleting rubric: ' + error.toString());
    return { success: false, error: error.toString() };
  }
}

/**
 * Get list of rubric names for dropdown
 */
function getRubricList() {
  var rubrics = getAllRubrics();
  var list = [];

  for (var id in rubrics) {
    list.push({
      id: id,
      name: rubrics[id].name,
      updatedAt: rubrics[id].updatedAt
    });
  }

  // Sort by most recently updated
  list.sort(function(a, b) {
    return new Date(b.updatedAt) - new Date(a.updatedAt);
  });

  return list;
}

/**
 * Validate rubric structure
 */
function validateRubric(rubric) {
  if (!rubric.name || rubric.name.trim() === '') {
    return { valid: false, error: 'Rubric name is required' };
  }

  if (!rubric.criteria || rubric.criteria.length === 0) {
    return { valid: false, error: 'At least one criterion is required' };
  }

  for (var i = 0; i < rubric.criteria.length; i++) {
    var criterion = rubric.criteria[i];
    if (!criterion.label || !criterion.description) {
      return { valid: false, error: 'Each criterion needs a label and description' };
    }
  }

  return { valid: true };
}
