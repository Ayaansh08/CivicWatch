import { useEffect, useState } from "react";
import { createComplaint, fetchCategories } from "./api";
import "./citizen.css";

function ComplaintForm() {
  const [form, setForm] = useState({
    title: "",
    description: "",
    category_id: "",
    latitude: "",
    longitude: "",
  });

  const [categories, setCategories] = useState([]);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState("");
  const [apiError, setApiError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadCategories() {
      try {
        const data = await fetchCategories();
        setCategories(data);
      } catch (error) {
        setApiError(error.message);
      }
    }

    loadCategories();
  }, []);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  function validateForm() {
    const newErrors = {};

    if (!form.title.trim()) {
      newErrors.title = "Title is required";
    } else if (form.title.trim().length < 5) {
      newErrors.title = "Title must be at least 5 characters";
    }

    if (!form.description.trim()) {
      newErrors.description = "Description is required";
    }

    if (!form.category_id) {
      newErrors.category_id = "Please choose a category";
    }

    return newErrors;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setMessage("");
    setApiError("");

    const validationErrors = validateForm();
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    const complaintData = {
      title: form.title.trim(),
      description: form.description.trim(),
      category_id: Number(form.category_id),
      latitude: form.latitude === "" ? null : Number(form.latitude),
      longitude: form.longitude === "" ? null : Number(form.longitude),
    };

    setLoading(true);

    try {
      await createComplaint(complaintData);
      setMessage("Complaint submitted");
      setForm({
        title: "",
        description: "",
        category_id: "",
        latitude: "",
        longitude: "",
      });
      setErrors({});
    } catch (error) {
      setApiError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="complaint-page">
      <h1>Report a Complaint</h1>

      <form onSubmit={handleSubmit} noValidate>
        <div className="form-field">
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={handleChange}
          />
          {errors.title && <p role="alert">{errors.title}</p>}
        </div>

        <div className="form-field">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
          />
          {errors.description && (
            <p role="alert">{errors.description}</p>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="category_id">Category</label>
          <select
            id="category_id"
            name="category_id"
            value={form.category_id}
            onChange={handleChange}
          >
            <option value="">Choose a category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
          {errors.category_id && (
            <p role="alert">{errors.category_id}</p>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="latitude">Latitude (optional)</label>
          <input
            id="latitude"
            name="latitude"
            type="number"
            step="any"
            value={form.latitude}
            onChange={handleChange}
          />
        </div>

        <div className="form-field">
          <label htmlFor="longitude">Longitude (optional)</label>
          <input
            id="longitude"
            name="longitude"
            type="number"
            step="any"
            value={form.longitude}
            onChange={handleChange}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>

      {message && <p role="status">{message}</p>}
      {apiError && <p role="alert">{apiError}</p>}
    </main>
  );
}

export default ComplaintForm;
