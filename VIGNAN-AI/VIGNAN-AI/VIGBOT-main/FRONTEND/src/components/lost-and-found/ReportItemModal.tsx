import React, { useState } from "react";
import { X, UploadCloud, AlertCircle } from "lucide-react";

interface ReportItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    type: 'lost' | 'found';
    title: string;
    description: string;
    tags: string;
    contactInfo: string;
    imageUrl?: string;
  }) => Promise<void>;
}

export const ReportItemModal: React.FC<ReportItemModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [type, setType] = useState<'lost' | 'found'>('lost');
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Client-side compression to avoid Next.js server action payload limits
    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;
        
        // Max dimensions
        const MAX_WIDTH = 800;
        const MAX_HEIGHT = 800;
        
        if (width > height) {
          if (width > MAX_WIDTH) {
            height *= MAX_WIDTH / width;
            width = MAX_WIDTH;
          }
        } else {
          if (height > MAX_HEIGHT) {
            width *= MAX_HEIGHT / height;
            height = MAX_HEIGHT;
          }
        }
        
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(img, 0, 0, width, height);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.7);
          setImageUrl(dataUrl);
        }
      };
      img.src = event.target?.result as string;
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    await onSubmit({ type, title, description, tags, contactInfo, imageUrl });
    setIsSubmitting(false);
    onClose();
    // Reset form
    setTitle("");
    setDescription("");
    setTags("");
    setContactInfo("");
    setImageUrl("");
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg overflow-hidden rounded-2xl bg-card shadow-2xl animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/50 px-6 py-4">
          <div>
            <h2 className="text-lg font-bold text-foreground">Report an Item</h2>
            <p className="text-sm text-muted-foreground mt-0.5">
              Lost something? Found something? Let the community know.
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-full p-2 text-slate-400 hover:bg-slate-200 hover:text-slate-600 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setType('lost')}
              className={`flex-1 rounded-xl py-3 text-sm font-bold border-2 transition-colors ${
                type === 'lost' 
                  ? 'border-rose-500 bg-rose-50 text-rose-700' 
                  : 'border-slate-200 bg-slate-50 text-slate-500 hover:border-slate-300'
              }`}
            >
              I Lost Something
            </button>
            <button
              type="button"
              onClick={() => setType('found')}
              className={`flex-1 rounded-xl py-3 text-sm font-bold border-2 transition-colors ${
                type === 'found' 
                  ? 'border-emerald-500 bg-emerald-50 text-emerald-700' 
                  : 'border-slate-200 bg-slate-50 text-slate-500 hover:border-slate-300'
              }`}
            >
              I Found Something
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Item Name
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Blue Milton Water Bottle"
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all bg-slate-50 focus:bg-white"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Description & Location
              </label>
              <textarea
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Where did you last see it or find it? Describe any unique features."
                rows={3}
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all bg-slate-50 focus:bg-white resize-none"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Tags (Comma separated)
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="e.g., electronics, keys, library"
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all bg-slate-50 focus:bg-white"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-bold text-slate-700 uppercase tracking-wider">
                Contact Information
              </label>
              <input
                type="text"
                required
                value={contactInfo}
                onChange={(e) => setContactInfo(e.target.value)}
                placeholder="Email or phone number"
                className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all bg-slate-50 focus:bg-white"
              />
            </div>

            <div className="relative rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 flex flex-col items-center justify-center text-center hover:bg-slate-100 transition-colors cursor-pointer overflow-hidden">
               {imageUrl ? (
                 <img src={imageUrl} alt="Uploaded preview" className="absolute inset-0 w-full h-full object-cover opacity-30" />
               ) : null}
               <div className="relative z-10 flex flex-col items-center">
                 <UploadCloud className="h-8 w-8 text-slate-400 mb-2" />
                 <p className="text-sm font-medium text-slate-700">{imageUrl ? 'Change Image' : 'Upload an Image'}</p>
                 <p className="text-xs text-slate-500 mt-1">Click to browse or drag and drop</p>
               </div>
               <input 
                 type="file" 
                 accept="image/*" 
                 onChange={handleImageUpload}
                 className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
               />
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-xl px-4 py-2.5 text-sm font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 rounded-xl px-4 py-2.5 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 transition-colors disabled:opacity-50 flex justify-center items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-white/20 border-t-white animate-spin" />
                  Submitting...
                </>
              ) : (
                "Post to Board"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
