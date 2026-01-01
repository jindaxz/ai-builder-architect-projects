const form = document.querySelector("#download-form");
const statusEl = document.querySelector("#status");
const submitBtn = form.querySelector('button[type="submit"]');

const setStatus = (message, variant = "") => {
  statusEl.textContent = message;
  statusEl.className = variant ? variant : "";
};

const toggleLoading = (isLoading) => {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle("is-loading", isLoading);
  if (isLoading) {
    setStatus("正在向 Instagram 请求数据...", "loading");
  }
};

const filenameFromDisposition = (disposition) => {
  if (!disposition) {
    return null;
  }
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return match ? match[1] : null;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = {
    username: (formData.get("username") || "").trim(),
    max_posts: Number(formData.get("max_posts")) || 12,
  };

  if (!payload.username) {
    setStatus("请输入要下载的 Instagram 用户名。", "error");
    return;
  }

  toggleLoading(true);

  try {
    const response = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type") || "";
    if (!response.ok) {
      if (contentType.includes("application/json")) {
        const data = await response.json();
        throw new Error(data.error || "下载失败");
      }
      throw new Error("下载失败，请稍后再试。");
    }

    if (contentType.includes("application/json")) {
      const data = await response.json();
      throw new Error(data.error || "无法生成下载文件。");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download =
      filenameFromDisposition(response.headers.get("Content-Disposition")) ||
      `${payload.username}_images.zip`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    setStatus("下载已开始，zip 文件包含最新的帖子图片。", "success");
  } catch (error) {
    setStatus(error.message || "下载失败，请稍后再试。", "error");
  } finally {
    toggleLoading(false);
  }
});
