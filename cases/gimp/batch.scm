; batch.scm — GIMP 2.10 Script-Fu
; Batch-normalize, mask, and export a dataset for AI building segmentation.
; Invoke:
;   gimp -i -b '(batch-prepare-dataset "assets/gimp/tiles" "assets/gimp/out")' -b '(gimp-quit 0)'

(define (batch-prepare-dataset in-dir out-dir)
  (let* ((files (cadr (file-glob (string-append in-dir "/*.png") 1))))
    (for-each
      (lambda (path)
        (let* ((img   (car (gimp-file-load RUN-NONINTERACTIVE path path)))
               (draw  (car (gimp-image-get-active-drawable img)))
               (base  (car (gimp-image-get-name img))))
          ; 1. auto levels (normalize exposure)
          (gimp-levels-stretch draw)
          ; 2. unsharp mask (mild, radius 1.2, amount 0.4)
          (plug-in-unsharp-mask RUN-NONINTERACTIVE img draw 1.2 0.4 0)
          ; 3. flatten + export PNG
          (gimp-image-flatten img)
          (file-png-save RUN-NONINTERACTIVE img
                         (car (gimp-image-get-active-drawable img))
                         (string-append out-dir "/" base)
                         base 0 9 1 1 1 1 1)
          (gimp-image-delete img)))
      files)))
