import { app } from "/scripts/app.js";
import { api } from '/scripts/api.js';

// Helper for creating elements
function createElement(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    Object.assign(el, attrs);
    children.forEach(child => el.appendChild(typeof child === 'string' ? document.createTextNode(child) : child));
    return el;
}

app.registerExtension({
    name: "RunningHub.LoadAudioPath",

    nodeCreated(node) {
        if (node.comfyClass !== "RH_LoadAudioPath") {
            return;
        }

        // Find the widget that holds the filename
        const filenameWidget = node.widgets.find((w) => w.name === "audio_filename");
        if (!filenameWidget) {
            console.error("RH_LoadAudioPath: Could not find 'audio_filename' widget on node:", node.id);
            return;
        }

        // --- Create Custom UI Elements ---
        const container = document.createElement("div");
        container.style.cssText = "padding: 8px 0;";

        const uploadButton = createElement("button", {
            textContent: "选择音频文件",
            style: "width: 100%; padding: 6px 8px; margin-bottom: 10px; font-size: 12px; cursor: pointer; border-radius: 4px;"
        });

        // Use <audio> element for preview
        const previewArea = createElement("div", {
            style: "width: 100%; background: #2a2a2a; border-radius: 6px; margin-bottom: 12px; overflow: hidden; display: none; padding: 8px;"
        });
        const previewAudio = createElement("audio", {
            controls: true,
            style: "width: 100%; display: block;"
        });
        const statusText = createElement("div", {
            textContent: "未选择音频",
            style: "padding: 5px 8px; font-size: 11px; color: #aaa; text-align: center; background: #1a1a1a; border-radius: 4px;"
        });

        previewArea.appendChild(previewAudio);
        container.appendChild(uploadButton);
        container.appendChild(previewArea);
        container.appendChild(statusText);

        node.addDOMWidget("audio_uploader_widget", "preview", container);

        // Function to upload file to ComfyUI backend
        async function uploadFileToComfyUI(file) {
            const shortName = file.name.length > 30 ? file.name.substring(0, 27) + "..." : file.name;
            statusText.textContent = `正在上传: ${shortName}`;
            statusText.style.color = "#2196F3";
            uploadButton.disabled = true;
            uploadButton.textContent = "上传中...";
            filenameWidget.value = "";

            try {
                const body = new FormData();
                body.append('image', file); // Still use 'image' key for ComfyUI endpoint
                
                const resp = await api.fetchApi("/upload/image", {
                    method: "POST",
                    body,
                });

                if (resp.status === 200 || resp.status === 201) {
                    const data = await resp.json();
                    if (data.name) {
                        const comfyFilename = data.subfolder ? `${data.subfolder}/${data.name}` : data.name;
                        filenameWidget.value = comfyFilename;
                        const displayName = data.name.length > 25 ? data.name.substring(0, 22) + "..." : data.name;
                        statusText.textContent = `已就绪: ${displayName}`;
                        statusText.style.color = "#4CAF50";
                        uploadButton.textContent = "已选择音频";
                        console.log(`RH_LoadAudioPath: ComfyUI upload successful: ${comfyFilename}`);
                    } else {
                        throw new Error("Filename not found in ComfyUI upload response.");
                    }
                } else {
                    throw new Error(`ComfyUI upload failed: ${resp.status} ${resp.statusText}`);
                }
            } catch (error) {
                console.error("RH_LoadAudioPath: ComfyUI upload error:", error);
                const errorMsg = error.message.length > 40 ? error.message.substring(0, 37) + "..." : error.message;
                statusText.textContent = `上传失败: ${errorMsg}`;
                statusText.style.color = "#f44336";
                filenameWidget.value = "ERROR";
            } finally {
                uploadButton.disabled = false;
                if (filenameWidget.value && filenameWidget.value !== "ERROR") {
                    uploadButton.textContent = "更换音频";
                } else {
                    uploadButton.textContent = "选择音频文件";
                    statusText.style.color = "#aaa";
                }
            }
        }

        // --- Event Listener for Button --- 
        uploadButton.addEventListener("click", () => {
            const fileInput = createElement("input", {
                type: "file",
                accept: "audio/mpeg,audio/ogg,audio/wav,audio/aac,audio/flac,audio/*",
                style: "display: none;"
            });

            fileInput.addEventListener("change", (event) => {
                const file = event.target.files[0];
                if (file) {
                    // Show preview using <audio> element
                    try {
                        const objectURL = URL.createObjectURL(file);
                        previewAudio.src = objectURL;
                        if (previewAudio.dataset.objectUrl) {
                            URL.revokeObjectURL(previewAudio.dataset.objectUrl);
                        }
                        previewAudio.dataset.objectUrl = objectURL;
                        previewArea.style.display = "block";
                    } catch (e) {
                        console.error("Error creating object URL for audio preview:", e);
                        previewArea.style.display = "none";
                        statusText.textContent = "预览失败，准备上传";
                        statusText.style.color = "#ff9800";
                    }

                    uploadFileToComfyUI(file);
                }
                fileInput.remove();
            });

            document.body.appendChild(fileInput);
            fileInput.click();
        });

        // Clean up object URL when node is removed
        const onRemoved = node.onRemoved;
        node.onRemoved = () => {
            if (previewAudio.dataset.objectUrl) {
                URL.revokeObjectURL(previewAudio.dataset.objectUrl);
            }
            onRemoved?.();
        };
    },
});
