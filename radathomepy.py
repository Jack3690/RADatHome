import astropy as astro
import astropy.stats as s
import astropy.visualization as viz
import astropy.units as u
import matplotlib.pyplot as plt
from astroquery.skyview import SkyView
import numpy as np
import photutils as phot
from astropy.wcs import WCS

class source_extract(object):
    def __init__(self, file):
        self.hdulist   = astro.io.fits.open(file)
        self.data      = (self.hdulist[0].data).squeeze()
        self.wcs       = WCS(self.hdulist[0].header)[0,0,:,:]
        self.hdulist.close()
        self.threshold = 0.015
        self.sigma     = 0.015
        self.sources   = self.detect()
        
    def detect(self):

        # Source detection using segmentation
        kernel = astro.convolution.Gaussian2DKernel(self.sigma, x_size=3, y_size=3)
        kernel.normalize()
        segm   = phot.detect_sources(self.data, self.threshold, npixels=5, filter_kernel=kernel)
        
        # Deblending sources
        segm_deblend = phot.deblend_sources(self.data, segm, npixels=5,
                                  filter_kernel=kernel, nlevels=32, contrast=0.001)
        
        cat = phot.source_properties(self.data,segm_deblend,wcs=self.wcs)
        sources = cat.to_table()
        sources['xcentroid'].info.format = '.2f'  # optional format
        sources['ycentroid'].info.format = '.2f'
        sources['cxx'].info.format       = '.2f'
        sources['cxy'].info.format       = '.2f'
        sources['cyy'].info.format       = '.2f'
        sources['gini'].info.format      = '.2f'
            
        return sources.to_pandas().sort_values('max_value',ascending=True)
   
    def get_positions(self):
        positions = []
        for i,j in zip(self.sources['sky_centroid_icrs.ra'], self.sources['sky_centroid_icrs.dec']):
            positions.append(f'{i}, {j}')
        return positions
            
    
    def write(self,filename):
        self.sources.to_csv(filename)

class RGB(object):
    def __init__(self, position,radius):
        self.position = position
        self.radius = radius
        self.surveys = ['DSS2 IR', 'DSS2 Red','DSS2 Blue','WISE 22','GALEX Near UV','TGSS ADR1','NVSS']
        self.img_dict = {
                            'Optical':[0, 1,2],
                            'IOU' :  [3,1,4],
                            'ROR' : [5, 1,6]
                        } 
        self.RGB_image ,self.contours, self.paths = self.RAD_RGB()
        self.levels = 4
        
    def make_RGB(self,survey ='Optical',cont='TGSS'):

        image = self.RGB_image[self.img_dict[survey]]
        image = np.stack((image[0],image[1],image[2]),axis=2)
        
        if cont=='TGSS':
            contour = self.contours[0]
            cont_min = 0.015
            c=5
        elif cont=='NVSS':
            contour = self.contours[1]
            c=6
            cont_min = 0.0015
        
        img_wcs= WCS(self.paths[self.img_dict[survey][0]][0].header)
        cont_wcs = WCS(self.paths[c][0].header)
        
        fig = plt.figure(figsize = (10,10))
        ax=fig.add_subplot(projection = img_wcs)
        ax.imshow(image)
        ax.set_autoscale_on(False)
 
        levels_c=np.arange(cont_min,contour.max(),(contour.max()-cont_min)/self.levels)
        ax.contour(contour, transform=ax.get_transform(cont_wcs), colors='white',levels=levels_c)
        
        ax.set_title(f'{survey} RGB with {cont} contours')
 
        return fig,ax
    
    def make_dataset(self):
        image = self.RGB_image[self.img_dict['IOU']]
        image = np.stack((image[0],image[1],image[2]),axis=2)
        
        img_wcs= WCS(self.paths[self.img_dict['IOU'][0]][0].header)
        
        cont_TGSS = self.contours[0]
        cont_wcs_TGSS = WCS(self.paths[5][0].header)
        
        cont_NVSS = self.contours[1]
        cont_wcs_NVSS = WCS(self.paths[6][0].header)
        
        fig = plt.figure(figsize = (10,10))
        ax=fig.add_subplot(projection = img_wcs)
        ax.imshow(image)
        ax.set_autoscale_on(False)
 
        levels_c=np.arange(0.015,cont_TGSS.max(),(cont_TGSS.max()-0.015)/self.levels)
        ax.contour(cont_TGSS, transform=ax.get_transform(cont_wcs_TGSS), colors='red',levels=levels_c)
        
        levels_c=np.arange(0.0015,cont_NVSS.max(),(cont_NVSS.max()-0.0015)/self.levels)
        ax.contour(cont_NVSS, transform=ax.get_transform(cont_wcs_NVSS), colors='blue',levels=levels_c)
        
        ax.set_title("IOU RGB with contours | TGSS : Red, NVSS : Blue")
        
        return fig,ax

    def RAD_RGB(self):
        try:
            paths_v = SkyView.get_images(position=self.position,pixels=600,scaling="Log",radius=self.radius*u.degree,survey=self.surveys[:-2])
            paths_r = SkyView.get_images(position=self.position,pixels=600,scaling="Sqrt",sampler='Lanczos3',radius=self.radius*u.degree,survey=self.surveys[-2:])
        except:    
            paths_v=[]
            for i in range(5):
                try:
                    path = SkyView.get_images(position=self.position,pixels=600,scaling="Log",radius=self.radius*u.degree,survey=self.surveys[i])
                    paths_v.append(path[0])
                except:
                    print(f"Data not found for {self.surveys[i]}")
                    paths_v.append([0])
            paths_r=[]
            for i in range(5,7):
                try:
                    path = SkyView.get_images(position=self.position,pixels=600,scaling="Sqrt",sampler='Lanczos3',radius=self.radius*u.degree,survey=self.surveys[i])
                    paths_r.append(path[0])
                except:
                    print(f"Data not found for {self.surveys[i]}")
                    paths_r.append([0])
     
        paths = paths_v + paths_r
      
        RGB=[]
        for path in paths:
            if path[0]==0:
                RGB.append(np.zeros((600,600)))
            else:    
                img=path[0].data.copy()
    
                min=img.min()
                img=img-min
    
                max=img.max()
                RGB.append(img/max)
        RGB_all=np.array(RGB)  
     
        contour=[]
        for path in paths_r:
            if path[0]==0:
                contour.append(np.zeros((600,600)))
            else:
                img=path[0].data.copy()
                contour.append(img)
        contour = np.array(contour)
        
        return RGB_all, contour, paths 
